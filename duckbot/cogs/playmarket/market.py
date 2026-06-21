import math
from decimal import ROUND_DOWN, Decimal
from typing import List, Literal, Optional

from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands, tasks
from sqlalchemy import String, cast, or_

from duckbot.db import Database
from duckbot.util.datetime import now

from . import config, lmsr
from .models import LedgerEntry, Market, PlayerAccount, Position, Season, SeasonResult

CENT = Decimal("0.000001")


def _down(value: float) -> Decimal:
    """Round a share count down to storage precision."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_DOWN)


def _whole(value) -> int:
    """Floor a coin amount to a whole coin (house keeps the fraction)."""
    return math.floor(value)


class PlayMarket(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.tick_loop.start()

    def cog_unload(self):
        self.tick_loop.cancel()

    # --- background season rollover ---------------------------------------

    @tasks.loop(hours=6)
    async def tick_loop(self):
        await self.tick()

    @tick_loop.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()

    async def tick(self):
        """Roll the season over when its time comes; markets are resolved by their creators."""
        with self.db.session(Season) as session:
            self.active_season(session)
            self.settle_season_if_due(session)
            session.commit()

    # --- command group ----------------------------------------------------

    @commands.hybrid_group(name="market", description="Gamble your friendship away on play-money bets.", invoke_without_command=True)
    async def market_group(self, context: commands.Context, status: Optional[str] = None):
        await self.list_markets(context, status)

    # --- economy commands -------------------------------------------------

    @market_group.command(name="balance", description="Show your coins and open positions.")
    async def balance_command(self, context: commands.Context):
        await self.balance(context)

    async def balance(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            account = self.account(session, season.id, context.author.id)
            rows = session.query(Position, Market).join(Market, Position.market_id == Market.id).filter(Position.user_id == account.id, Market.status == "OPEN").order_by(Market.id.desc()).all()
            session.commit()
            lines = [f"**{self._name(context, account.id)}** — {_coins(account.balance)} coins"]
            lines += [f"**{m.id}** {m.question} — YES {_pct(self._price(m))} · you hold {_coins(p.yes_shares)} YES / {_coins(p.no_shares)} NO" for p, m in rows if p.yes_shares or p.no_shares]
        await context.send("\n".join(lines))

    @market_group.command(name="claim", description="Claim the need-based top-up if you are broke and have no open positions.")
    async def claim_command(self, context: commands.Context):
        await self.claim(context)

    async def claim(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            account = self.account(session, season.id, context.author.id)
            if account.balance >= config.TOPUP_THRESHOLD:
                return await context.send("Quit begging, you're not even broke.")
            if session.query(Position).filter_by(user_id=account.id).filter((Position.yes_shares > 0) | (Position.no_shares > 0)).first():
                return await context.send("You've got open bets, brother. No charity for gamblers.")
            if account.last_topup_at and now() < account.last_topup_at + config.TOPUP_COOLDOWN:
                return await context.send("Already milked that cow this week, greedy.")
            grant = config.TOPUP_TARGET - account.balance
            account.last_topup_at = now()
            self._credit(session, season.id, account, None, grant, "topup")
            session.commit()
            await context.send(f"Pity money granted. You're sitting on {_coins(account.balance)} coins now, you charity case.")

    @market_group.command(name="leaderboard", description="Current-season standings by net worth.")
    async def leaderboard_command(self, context: commands.Context):
        await self.leaderboard(context)

    async def leaderboard(self, context: commands.Context):
        with self.db.session(Season) as session:
            ranked = self._standings(session)
            session.commit()
        if not ranked:
            return await context.send("Nobody's played yet. Buncha cowards.")
        lines = [f"{i}. {self._name(context, uid)} — {_coins(worth)} coins" for i, (uid, worth) in enumerate(ranked, start=1)]
        await context.send("**Leaderboard**\n" + "\n".join(lines))

    # --- market commands --------------------------------------------------

    @market_group.command(name="list", description="List markets with their current YES %.")
    async def list_command(self, context: commands.Context, status: Optional[str] = None):
        await self.list_markets(context, status)

    async def list_markets(self, context: commands.Context, status: Optional[str]):
        with self.db.session(Market) as session:
            query = session.query(Market).filter(Market.status == (status.upper() if status else "OPEN"))
            markets = query.order_by(Market.id.desc()).all()
        if not markets:
            return await context.send("No markets. What, you hate fun?")
        await context.send("\n".join(self._summary(m) for m in markets))

    @market_group.command(name="create", description="Create a YES/NO market you'll resolve yourself.")
    async def create_command(self, context: commands.Context, question: str, liquidity: Literal["low", "med", "high"] = "med"):
        await self.create(context, question, liquidity)

    async def create(self, context: commands.Context, question: str, liquidity: str):
        b = config.LIQUIDITY[liquidity]
        with self.db.session(Season) as session:
            season = self.active_season(session)
            if season.status != "active":
                return await context.send("Season's wrapping up, no new markets. Pump the brakes.")
            self.account(session, season.id, context.author.id)  # ensure creator has an account
            market = Market(season_id=season.id, creator_id=context.author.id, question=question, b=b, subsidy=_whole(lmsr.subsidy(b)))
            session.add(market)
            session.commit()
            await context.send(f"Market **{market.id}** is live: _{question}_ — YES 50%. Place your bets, degenerates.")

    @market_group.command(name="bet", description="Buy YES/NO shares for a coin budget.")
    async def bet_command(self, context: commands.Context, market: int, side: Literal["yes", "no"], amount: int):
        await self.bet(context, market, side, amount)

    async def bet(self, context: commands.Context, market_id: int, side: str, amount: int):
        cost = int(amount)
        if cost < config.MIN_BET:
            return await context.send(f"{_coins(config.MIN_BET)} coins minimum, you cheapskate.")
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market, brother.")
            if market.status != "OPEN":
                return await context.send("That market's done. Ship's sailed, brother.")
            account = self.account(session, market.season_id, context.author.id)
            if account.balance < cost:
                return await context.send(f"Broke boy. You've only got {_coins(account.balance)} coins.")
            shares = _down(lmsr.shares_for_budget(float(market.q_yes), float(market.q_no), float(market.b), side, amount))
            self._credit(session, market.season_id, account, market.id, -cost, "bet")
            self._add_shares(session, market, context.author.id, side, shares)
            session.commit()
            await context.send(f"Bought {_coins(shares)} {side.upper()} shares for {_coins(cost)} coins. YES is now {_pct(self._price(market))}.")

    @market_group.command(name="sell", description="Sell held shares back to the market.")
    async def sell_command(self, context: commands.Context, market: int, side: Literal["yes", "no"], shares: str):
        await self.sell(context, market, side, shares)

    async def sell(self, context: commands.Context, market_id: int, side: str, shares: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market, brother.")
            if market.status != "OPEN":
                return await context.send("That market's done. Ship's sailed, brother.")
            position = session.get(Position, (context.author.id, market_id))
            held = (position.yes_shares if side == "yes" else position.no_shares) if position else Decimal(0)
            amount = held if shares == "all" else Decimal(str(shares))
            if amount <= 0 or amount > held:
                return await context.send(f"You've only got {_coins(held)} {side.upper()} shares, brother.")
            account = self.account(session, market.season_id, context.author.id)
            proceeds = self._sell_proceeds(market, side, amount)
            self._add_shares(session, market, context.author.id, side, -amount)
            self._credit(session, market.season_id, account, market.id, proceeds, "sell")
            session.commit()
            await context.send(f"Sold {_coins(amount)} {side.upper()} shares for {_coins(proceeds)} coins. YES is now {_pct(self._price(market))}.")

    @market_group.command(name="resolve", description="Resolve your market and pay everyone out (creator only).")
    async def resolve_command(self, context: commands.Context, market: int, outcome: Literal["yes", "no", "void"]):
        await self.resolve(context, market, outcome)

    @bet_command.autocomplete("market")
    @sell_command.autocomplete("market")
    @resolve_command.autocomplete("market")
    async def market_autocomplete(self, interaction: Interaction, current: str) -> List[Choice[int]]:
        needle = f"%{current}%"
        with self.db.session(Market) as session:
            matches = session.query(Market.id, Market.question)
            matches = matches.filter(Market.status == "OPEN", or_(Market.question.ilike(needle), cast(Market.id, String).ilike(needle)))
            matches = matches.order_by(Market.id.desc()).limit(25).all()  # Discord caps options at 25
        return [Choice(name=f"{mid}: {q}"[:100], value=mid) for mid, q in matches]

    async def resolve(self, context: commands.Context, market_id: int, outcome: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market, brother.")
            if market.status != "OPEN":
                return await context.send("That one's already in the books, brother.")
            if context.author.id != market.creator_id and not await self._is_admin(context):
                return await context.send("Not your market, not your call.")
            self._resolve_market(session, market, outcome)
            session.commit()
            await context.send(f"Market {market_id} called **{outcome.upper()}**. Winners paid, losers weep.")

    # --- season lifecycle -------------------------------------------------

    def active_season(self, session) -> Season:
        """The active or settling season; creates Season 1 on first use, flips ended ones to settling."""
        season = session.query(Season).filter(Season.status.in_(("active", "settling"))).order_by(Season.id.desc()).first()
        if season is None:
            return self._new_season(session)
        if season.status == "active" and now() >= season.ends_at:
            season.status = "settling"
        return season

    def settle_season_if_due(self, session):
        """After the grace period, void unresolved markets and roll over to the next season."""
        season = session.query(Season).filter_by(status="settling").first()
        if season is None or now() < season.ends_at + config.SETTLEMENT_GRACE:
            return
        for market in session.query(Market).filter(Market.season_id == season.id, Market.status == "OPEN").all():
            self._resolve_market(session, market, "void")
        accounts = session.query(PlayerAccount).all()
        for rank, account in enumerate(sorted(accounts, key=lambda a: a.balance, reverse=True), start=1):
            session.add(SeasonResult(season_id=season.id, user_id=account.id, final_balance=account.balance, rank=rank))
        season.status = "archived"
        next_season = self._new_season(session)
        for account in accounts:
            account.balance = 0
            self._credit(session, next_season.id, account, None, config.STARTING_BALANCE, "season_grant")

    def _new_season(self, session) -> Season:
        count = session.query(Season).count()
        season = Season(name=f"Season {count + 1}", starts_at=now(), ends_at=now() + config.SEASON_LENGTH, status="active", starting_balance=config.STARTING_BALANCE)
        session.add(season)
        session.flush()  # assign id
        return season

    # --- money mechanics ---------------------------------------------------

    def account(self, session, season_id: int, user_id: int) -> PlayerAccount:
        """The player's account, granting the starting balance on first sight."""
        account = self._lock_account(session, user_id)
        if account is None:
            account = PlayerAccount(id=user_id, balance=0)
            session.add(account)
            session.flush()
            self._credit(session, season_id, account, None, config.STARTING_BALANCE, "season_grant")
        return account

    def _credit(self, session, season_id, account, market_id, delta, reason):
        """Apply a balance delta and write the matching ledger row."""
        account.balance += delta
        session.add(LedgerEntry(season_id=season_id, user_id=account.id, market_id=market_id, delta=delta, reason=reason))

    def _resolve_market(self, session, market, outcome):
        """Pay out winning shares (0.5 each on void), close positions, finalise."""
        for position in session.query(Position).filter_by(market_id=market.id).all():
            payout = self._payout(position, outcome)
            if payout > 0:
                account = self._lock_account(session, position.user_id)
                self._credit(session, market.season_id, account, market.id, payout, "refund" if outcome == "void" else "payout")
            session.delete(position)
        market.status = "VOID" if outcome == "void" else "RESOLVED"
        market.outcome = outcome

    def _payout(self, position, outcome) -> int:
        if outcome == "void":
            shares = (position.yes_shares + position.no_shares) / 2
        else:
            shares = position.yes_shares if outcome == "yes" else position.no_shares
        return _whole(shares)

    def _add_shares(self, session, market, user_id, side, delta):
        position = session.get(Position, (user_id, market.id)) or Position(user_id=user_id, market_id=market.id, yes_shares=Decimal(0), no_shares=Decimal(0))
        session.add(position)
        if side == "yes":
            position.yes_shares += delta
            market.q_yes += delta
        else:
            position.no_shares += delta
            market.q_no += delta

    def _sell_proceeds(self, market, side, amount) -> int:
        before = lmsr.cost(float(market.q_yes), float(market.q_no), float(market.b))
        q_yes = float(market.q_yes) - (float(amount) if side == "yes" else 0)
        q_no = float(market.q_no) - (float(amount) if side == "no" else 0)
        return _whole(before - lmsr.cost(q_yes, q_no, float(market.b)))

    # --- read helpers -----------------------------------------------------

    def _standings(self, session):
        """(user_id, net worth) ranked high to low; net worth = balance + open position value."""
        worth = {a.id: a.balance for a in session.query(PlayerAccount).all()}
        rows = session.query(Position, Market).join(Market, Position.market_id == Market.id).filter(Market.status == "OPEN").all()
        for position, market in rows:
            yes_price = Decimal(str(self._price(market)))
            worth[position.user_id] = worth.get(position.user_id, Decimal(0)) + position.yes_shares * yes_price + position.no_shares * (1 - yes_price)
        return sorted(worth.items(), key=lambda kv: kv[1], reverse=True)

    def _lock_market(self, session, market_id) -> Optional[Market]:
        return session.query(Market).filter_by(id=market_id).with_for_update().first()

    def _lock_account(self, session, user_id) -> Optional[PlayerAccount]:
        return session.query(PlayerAccount).filter_by(id=user_id).with_for_update().first()

    def _price(self, market) -> float:
        return lmsr.price_yes(float(market.q_yes), float(market.q_no), float(market.b))

    def _summary(self, market) -> str:
        return f"**{market.id}** [{market.status}] {market.question} — YES {_pct(self._price(market))}"

    async def _is_admin(self, context) -> bool:
        return await context.bot.is_owner(context.author) or context.author.id in config.ADMIN_IDS

    def _name(self, context, user_id) -> str:
        member = context.guild.get_member(user_id) if context.guild else None
        user = member or self.bot.get_user(user_id)
        return user.display_name if user else str(user_id)


def _coins(value) -> str:
    return f"{value:,.0f}"


def _pct(probability: float) -> str:
    return f"{probability * 100:.0f}%"
