import re
from datetime import datetime, timedelta
from decimal import ROUND_DOWN, Decimal
from typing import Literal, Optional

from discord.ext import commands, tasks

from duckbot.db import Database
from duckbot.util.datetime import now, timezone

from . import config, lmsr
from .models import (
    LedgerEntry,
    Market,
    PlayerAccount,
    Position,
    Proposal,
    Season,
    SeasonResult,
)

CENT = Decimal("0.000001")
TRADING = ("OPEN", "CLOSED", "PROPOSED", "DISPUTED")  # market is live; positions still have value


def _down(value: float) -> Decimal:
    """Quantise to storage precision, rounding toward the house so solvency always holds."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_DOWN)


def parse_when(text: str) -> Optional[datetime]:
    """Parse a close time: `in 3 days` / `in 6 hours` / `in 2 weeks`, or `YYYY-MM-DD[ HH:MM]`."""
    relative = re.fullmatch(r"in (\d+) (hour|day|week)s?", text.strip().lower())
    if relative:
        amount, unit = int(relative.group(1)), relative.group(2)
        return now() + {"hour": timedelta(hours=amount), "day": timedelta(days=amount), "week": timedelta(weeks=amount)}[unit]
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text.strip(), fmt).replace(tzinfo=timezone())
        except ValueError:
            continue
    return None


async def is_market_admin(context: commands.Context) -> bool:
    """Only the bot owner or someone who can manage the server may break disputes."""
    if context.guild is None:
        raise commands.NoPrivateMessage()
    if not await context.bot.is_owner(context.author) and not context.author.guild_permissions.manage_guild:
        raise commands.MissingPermissions(["manage server"])
    return True


class PlayMarket(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.tick_loop.start()

    def cog_unload(self):
        self.tick_loop.cancel()

    # --- background timing ------------------------------------------------

    @tasks.loop(minutes=1)
    async def tick_loop(self):
        await self.tick()

    @tick_loop.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()

    async def tick(self):
        """Advance everything time can change: close markets, finalise proposals, roll seasons over."""
        with self.db.session(Season) as session:
            self.active_season(session)
            for market in session.query(Market).filter(Market.status.in_(("OPEN", "PROPOSED"))).all():
                self.advance(session, market)
            self.settle_season_if_due(session)
            session.commit()

    # --- economy commands -------------------------------------------------

    @commands.hybrid_command(name="balance", description="Show your coins, locked bonds, and open positions.")
    async def balance_command(self, context: commands.Context):
        await self.balance(context)

    async def balance(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            account = self.account(session, season.id, context.author.id)
            positions = session.query(Position).filter_by(user_id=account.id).all()
            session.commit()
            lines = [f"**{self._name(context, account.id)}** — {_coins(account.balance)} coins (+{_coins(account.locked)} locked in bonds)"]
            lines += [f"• market {p.market_id}: {_coins(p.yes_shares)} YES / {_coins(p.no_shares)} NO" for p in positions if p.yes_shares or p.no_shares]
        await context.send("\n".join(lines))

    @commands.hybrid_command(name="claim", description="Claim the need-based top-up if you are broke and have no open positions.")
    async def claim_command(self, context: commands.Context):
        await self.claim(context)

    async def claim(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            account = self.account(session, season.id, context.author.id)
            if account.balance >= config.TOPUP_THRESHOLD:
                return await context.send(f"You only qualify when your balance is under {_coins(config.TOPUP_THRESHOLD)}.")
            if session.query(Position).filter_by(user_id=account.id).filter((Position.yes_shares > 0) | (Position.no_shares > 0)).first():
                return await context.send("Sell or resolve your open positions before claiming.")
            if account.last_topup_at and now() < account.last_topup_at + config.TOPUP_COOLDOWN:
                return await context.send("You already claimed this week.")
            grant = config.TOPUP_TARGET - account.balance
            account.last_topup_at = now()
            self._credit(session, season.id, account, None, grant, "topup")
            session.commit()
            await context.send(f"Topped up to {_coins(account.balance)} coins. Bet wisely.")

    @commands.hybrid_command(name="leaderboard", description="Current-season standings by net worth.")
    async def leaderboard_command(self, context: commands.Context):
        await self.leaderboard(context)

    async def leaderboard(self, context: commands.Context):
        with self.db.session(Season) as session:
            ranked = self._standings(session)
            session.commit()
        if not ranked:
            return await context.send("Nobody has played yet.")
        lines = [f"{i}. {self._name(context, uid)} — {_coins(worth)} coins" for i, (uid, worth) in enumerate(ranked, start=1)]
        await context.send("**Leaderboard**\n" + "\n".join(lines))

    @commands.hybrid_command(name="season", description="Show the active season and your rank.")
    async def season_command(self, context: commands.Context):
        await self.season(context)

    async def season(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            ranked = self._standings(session)
            session.commit()
            rank = next((i for i, (uid, _) in enumerate(ranked, start=1) if uid == context.author.id), None)
            remaining = season.ends_at - now()
            status = "ending soon — no new markets" if season.status == "settling" else f"{remaining.days} days left"
        await context.send(f"**{season.name}** ({status}). Your rank: {rank or 'unranked'} of {len(ranked)}.")

    # --- market commands --------------------------------------------------

    @commands.hybrid_group(name="market", invoke_without_command=True)
    async def market_group(self, context: commands.Context, status: Optional[str] = None):
        await self.list_markets(context, status)

    @market_group.command(name="list", description="List markets with their current YES %.")
    async def list_command(self, context: commands.Context, status: Optional[str] = None):
        await self.list_markets(context, status)

    async def list_markets(self, context: commands.Context, status: Optional[str]):
        with self.db.session(Market) as session:
            query = session.query(Market)
            if status:
                query = query.filter(Market.status == status.upper())
            else:
                query = query.filter(Market.status.in_(TRADING))
            markets = query.order_by(Market.id.desc()).limit(20).all()
        if not markets:
            return await context.send("No markets. Start one with `/market create`.")
        await context.send("\n".join(self._summary(m) for m in markets))

    @market_group.command(name="show", description="Show one market and your position in it.")
    async def show_command(self, context: commands.Context, market_id: int):
        await self.show(context, market_id)

    async def show(self, context: commands.Context, market_id: int):
        with self.db.session(Market) as session:
            market = session.get(Market, market_id)
            if market is None:
                return await context.send("No such market.")
            position = session.get(Position, (context.author.id, market_id))
            mine = f"\nYou hold {_coins(position.yes_shares)} YES / {_coins(position.no_shares)} NO." if position else ""
        await context.send(f"{self._summary(market)}\n_{market.rules}_{mine}")

    @market_group.command(name="create", description="Create a YES/NO market.")
    async def create_command(self, context: commands.Context, question: str, rules: str, closes: str, liquidity: Literal["low", "med", "high"] = "med"):
        await self.create(context, question, rules, closes, liquidity)

    async def create(self, context: commands.Context, question: str, rules: str, closes: str, liquidity: str):
        close_at = parse_when(closes)
        if close_at is None:
            return await context.send("I can't read that close time. Try `2025-07-01 18:00` or `in 3 days`.")
        if close_at <= now():
            return await context.send("The close time must be in the future.")
        b = config.LIQUIDITY[liquidity]
        with self.db.session(Season) as session:
            season = self.active_season(session)
            if season.status != "active":
                return await context.send("The season is wrapping up; no new markets right now.")
            if close_at > season.ends_at:
                return await context.send(f"Markets must close before the season ends ({_when(season.ends_at)}).")
            self.account(session, season.id, context.author.id)  # ensure creator has an account
            market = Market(season_id=season.id, creator_id=context.author.id, question=question, rules=rules, b=Decimal(str(b)), subsidy=_down(lmsr.subsidy(b)), close_at=close_at)
            session.add(market)
            session.commit()
            await context.send(f"Market **{market.id}** open: _{question}_ — YES 50%. Closes {_when(close_at)}.")

    @market_group.command(name="quote", description="Preview a bet without placing it.")
    async def quote_command(self, context: commands.Context, market_id: int, side: Literal["yes", "no"], amount: float):
        await self.quote(context, market_id, side, amount)

    async def quote(self, context: commands.Context, market_id: int, side: str, amount: float):
        with self.db.session(Market) as session:
            market = session.get(Market, market_id)
        if market is None or market.status != "OPEN":
            return await context.send("That market is not open for trading.")
        shares = lmsr.shares_for_budget(float(market.q_yes), float(market.q_no), float(market.b), side, amount)
        after = self._price_after(market, side, _down(shares))
        await context.send(f"{_coins(Decimal(str(amount)))} coins buys ~{_coins(_down(shares))} {side.upper()} shares; YES would move to {_pct(after)}.")

    @market_group.command(name="bet", description="Buy YES/NO shares for a coin budget.")
    async def bet_command(self, context: commands.Context, market_id: int, side: Literal["yes", "no"], amount: float):
        await self.bet(context, market_id, side, amount)

    async def bet(self, context: commands.Context, market_id: int, side: str, amount: float):
        cost = Decimal(str(amount))
        if cost < config.MIN_BET:
            return await context.send(f"Minimum bet is {_coins(config.MIN_BET)} coin.")
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market.")
            self.advance(session, market)
            if market.status != "OPEN":
                return await context.send("Market is closed for trading. Use `/market propose` to resolve it.")
            account = self.account(session, market.season_id, context.author.id)
            if account.balance < cost:
                return await context.send(f"You only have {_coins(account.balance)} coins.")
            shares = _down(lmsr.shares_for_budget(float(market.q_yes), float(market.q_no), float(market.b), side, amount))
            self._credit(session, market.season_id, account, market.id, -cost, "bet")
            self._add_shares(session, market, context.author.id, side, shares)
            session.commit()
            await context.send(f"Bought {_coins(shares)} {side.upper()} shares for {_coins(cost)} coins. YES is now {_pct(self._price(market))}.")

    @market_group.command(name="sell", description="Sell held shares back to the market.")
    async def sell_command(self, context: commands.Context, market_id: int, side: Literal["yes", "no"], shares: str):
        await self.sell(context, market_id, side, shares)

    async def sell(self, context: commands.Context, market_id: int, side: str, shares: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market.")
            self.advance(session, market)
            if market.status != "OPEN":
                return await context.send("Trading is closed on that market.")
            position = session.get(Position, (context.author.id, market_id))
            held = (position.yes_shares if side == "yes" else position.no_shares) if position else Decimal(0)
            amount = held if shares == "all" else Decimal(str(shares))
            if amount <= 0 or amount > held:
                return await context.send(f"You hold {_coins(held)} {side.upper()} shares.")
            account = self.account(session, market.season_id, context.author.id)
            proceeds = self._sell_proceeds(market, side, amount)
            self._add_shares(session, market, context.author.id, side, -amount)
            self._credit(session, market.season_id, account, market.id, proceeds, "sell")
            session.commit()
            await context.send(f"Sold {_coins(amount)} {side.upper()} shares for {_coins(proceeds)} coins. YES is now {_pct(self._price(market))}.")

    # --- resolution commands ---------------------------------------------

    @market_group.command(name="propose", description="Propose an outcome for a closed market (posts a bond).")
    async def propose_command(self, context: commands.Context, market_id: int, outcome: Literal["yes", "no"]):
        await self.propose(context, market_id, outcome)

    async def propose(self, context: commands.Context, market_id: int, outcome: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market.")
            self.advance(session, market)
            if market.status != "CLOSED":
                return await context.send("Only a closed, unresolved market can be proposed.")
            account = self.account(session, market.season_id, context.author.id)
            if account.balance < config.PROPOSE_BOND:
                return await context.send(f"You need {_coins(config.PROPOSE_BOND)} coins for the bond.")
            self._hold_bond(account, config.PROPOSE_BOND)
            session.add(Proposal(market_id=market_id, proposer_id=account.id, proposed=outcome, bond=config.PROPOSE_BOND, window_ends=now() + config.DISPUTE_WINDOW))
            market.status = "PROPOSED"
            session.commit()
            await context.send(f"Market {market_id} proposed **{outcome.upper()}**. Disputable for 24h with `/market dispute`.")

    @market_group.command(name="dispute", description="Dispute the proposed outcome (posts a matching bond).")
    async def dispute_command(self, context: commands.Context, market_id: int):
        await self.dispute(context, market_id)

    async def dispute(self, context: commands.Context, market_id: int):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None or market.status != "PROPOSED":
                return await context.send("There is no open proposal to dispute.")
            proposal = self._pending(session, market_id)
            if now() >= proposal.window_ends:
                self.advance(session, market)
                session.commit()
                return await context.send("The dispute window has closed; the market resolved to the proposal.")
            if proposal.proposer_id == context.author.id:
                return await context.send("You can't dispute your own proposal.")
            account = self.account(session, market.season_id, context.author.id)
            if account.balance < config.DISPUTE_BOND:
                return await context.send(f"You need {_coins(config.DISPUTE_BOND)} coins for the bond.")
            self._hold_bond(account, config.DISPUTE_BOND)
            proposal.disputer_id = account.id
            proposal.dispute_bond = config.DISPUTE_BOND
            proposal.status = "disputed"
            market.status = "DISPUTED"
            session.commit()
            await context.send(f"Market {market_id} disputed. An admin must `/market resolve` it.")

    @market_group.command(name="resolve", description="Admin: settle a disputed market and run payouts.")
    @commands.check(is_market_admin)
    async def resolve_command(self, context: commands.Context, market_id: int, outcome: Literal["yes", "no", "void"]):
        await self.resolve(context, market_id, outcome)

    async def resolve(self, context: commands.Context, market_id: int, outcome: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market.")
            self.advance(session, market)
            if market.status not in ("CLOSED", "PROPOSED", "DISPUTED"):
                return await context.send("That market can't be resolved until it closes.")
            proposal = self._pending(session, market_id)
            if proposal:
                proposal.resolver_id = context.author.id
                self._settle_bonds(session, market, proposal, outcome)
            self._resolve_market(session, market, outcome)
            session.commit()
            await context.send(f"Market {market_id} resolved **{outcome.upper()}**. Payouts done.")

    # --- season lifecycle -------------------------------------------------

    def active_season(self, session) -> Season:
        """Return the season scoping play, creating Season 1 on first use and flipping ended seasons to settling."""
        season = session.query(Season).filter(Season.status.in_(("active", "settling"))).order_by(Season.id.desc()).first()
        if season is None:
            return self._new_season(session)
        if season.status == "active" and now() >= season.ends_at:
            season.status = "settling"
        return season

    def settle_season_if_due(self, session):
        """After the grace period, force-void stragglers and roll into the next season."""
        season = session.query(Season).filter_by(status="settling").first()
        if season is None or now() < season.ends_at + config.SETTLEMENT_GRACE:
            return
        for market in session.query(Market).filter(Market.season_id == season.id, Market.status.notin_(("RESOLVED", "VOID"))).all():
            self._resolve_market(session, market, "void")
        accounts = session.query(PlayerAccount).all()
        for rank, account in enumerate(sorted(accounts, key=lambda a: a.balance, reverse=True), start=1):
            session.add(SeasonResult(season_id=season.id, user_id=account.id, final_balance=account.balance, rank=rank))
        season.status = "archived"
        next_season = self._new_season(session)
        for account in accounts:
            account.balance = Decimal(0)
            account.locked = Decimal(0)
            self._credit(session, next_season.id, account, None, config.STARTING_BALANCE, "season_grant")

    def _new_season(self, session) -> Season:
        count = session.query(Season).count()
        season = Season(name=f"Season {count + 1}", starts_at=now(), ends_at=now() + config.SEASON_LENGTH, status="active", starting_balance=config.STARTING_BALANCE)
        session.add(season)
        session.flush()  # assign id for use as a foreign key
        return season

    def advance(self, session, market: Market):
        """Apply time-driven transitions to one market (also done lazily on every touch)."""
        if market.status == "OPEN" and now() >= market.close_at:
            market.status = "CLOSED"
        elif market.status == "PROPOSED":
            proposal = self._pending(session, market.id)
            if proposal and now() >= proposal.window_ends:
                self._release_bond(self._lock_account(session, proposal.proposer_id), proposal.bond)
                proposal.status = "accepted"
                self._resolve_market(session, market, proposal.proposed)

    # --- money mechanics (the only places balances and the ledger change) ---

    def account(self, session, season_id: int, user_id: int) -> PlayerAccount:
        """Fetch the player's account (locked for update), granting the season's starting balance on first sight."""
        account = self._lock_account(session, user_id)
        if account is None:
            account = PlayerAccount(id=user_id, balance=Decimal(0), locked=Decimal(0))
            session.add(account)
            self._credit(session, season_id, account, None, config.STARTING_BALANCE, "season_grant")
        return account

    def _credit(self, session, season_id, account, market_id, delta, reason):
        """Change a balance and write the matching ledger row in one place, so they never drift apart."""
        account.balance += delta
        session.add(LedgerEntry(season_id=season_id, user_id=account.id, market_id=market_id, delta=delta, reason=reason))

    def _hold_bond(self, account, amount):
        account.balance -= amount
        account.locked += amount

    def _release_bond(self, account, amount):
        account.locked -= amount
        account.balance += amount

    def _settle_bonds(self, session, market, proposal, outcome):
        """Zero-sum bond settlement: the loser's bond moves to the winner; void returns both."""
        proposer = self._lock_account(session, proposal.proposer_id)
        disputer = self._lock_account(session, proposal.disputer_id) if proposal.disputer_id else None
        self._release_bond(proposer, proposal.bond)
        if disputer is None:
            proposal.status = "settled"
            return
        self._release_bond(disputer, proposal.dispute_bond)
        if outcome != "void":
            winner, loser, forfeit = (proposer, disputer, proposal.dispute_bond) if proposal.proposed == outcome else (disputer, proposer, proposal.bond)
            self._credit(session, market.season_id, loser, market.id, -forfeit, "bond")
            self._credit(session, market.season_id, winner, market.id, forfeit, "bond_win")
        proposal.status = "settled"

    def _resolve_market(self, session, market, outcome):
        """Pay winning shares (or 0.5 each on void), close positions, finalise the market."""
        for position in session.query(Position).filter_by(market_id=market.id).all():
            payout = self._payout(position, outcome)
            if payout > 0:
                account = self._lock_account(session, position.user_id)
                self._credit(session, market.season_id, account, market.id, payout, "refund" if outcome == "void" else "payout")
            session.delete(position)
        market.status = "VOID" if outcome == "void" else "RESOLVED"
        market.outcome = outcome

    def _payout(self, position, outcome) -> Decimal:
        if outcome == "void":
            return _down((position.yes_shares + position.no_shares) / 2)
        return position.yes_shares if outcome == "yes" else position.no_shares

    def _add_shares(self, session, market, user_id, side, delta):
        position = session.get(Position, (user_id, market.id)) or Position(user_id=user_id, market_id=market.id, yes_shares=Decimal(0), no_shares=Decimal(0))
        session.add(position)
        if side == "yes":
            position.yes_shares += delta
            market.q_yes += delta
        else:
            position.no_shares += delta
            market.q_no += delta

    def _sell_proceeds(self, market, side, amount) -> Decimal:
        before = lmsr.cost(float(market.q_yes), float(market.q_no), float(market.b))
        q_yes = float(market.q_yes) - (float(amount) if side == "yes" else 0)
        q_no = float(market.q_no) - (float(amount) if side == "no" else 0)
        return _down(before - lmsr.cost(q_yes, q_no, float(market.b)))

    # --- read helpers -----------------------------------------------------

    def _standings(self, session):
        """List of (user_id, net worth) ranked high to low; net worth = balance + value of open positions."""
        worth = {a.id: a.balance for a in session.query(PlayerAccount).all()}
        rows = session.query(Position, Market).join(Market, Position.market_id == Market.id).filter(Market.status.in_(TRADING)).all()
        for position, market in rows:
            yes_price = Decimal(str(self._price(market)))
            worth[position.user_id] = worth.get(position.user_id, Decimal(0)) + position.yes_shares * yes_price + position.no_shares * (1 - yes_price)
        return sorted(worth.items(), key=lambda kv: kv[1], reverse=True)

    def _lock_market(self, session, market_id) -> Optional[Market]:
        return session.query(Market).filter_by(id=market_id).with_for_update().first()

    def _lock_account(self, session, user_id) -> Optional[PlayerAccount]:
        return session.query(PlayerAccount).filter_by(id=user_id).with_for_update().first()

    def _pending(self, session, market_id) -> Optional[Proposal]:
        return session.query(Proposal).filter(Proposal.market_id == market_id, Proposal.status.in_(("pending", "disputed"))).first()

    def _price(self, market) -> float:
        return lmsr.price_yes(float(market.q_yes), float(market.q_no), float(market.b))

    def _price_after(self, market, side, shares) -> float:
        q_yes = float(market.q_yes) + (float(shares) if side == "yes" else 0)
        q_no = float(market.q_no) + (float(shares) if side == "no" else 0)
        return lmsr.price_yes(q_yes, q_no, float(market.b))

    def _summary(self, market) -> str:
        return f"**{market.id}** [{market.status}] {market.question} — YES {_pct(self._price(market))}"

    def _name(self, context, user_id) -> str:
        member = context.guild.get_member(user_id) if context.guild else None
        user = member or self.bot.get_user(user_id)
        return user.display_name if user else str(user_id)


def _coins(value) -> str:
    return f"{value:,.0f}"


def _pct(probability: float) -> str:
    return f"{probability * 100:.0f}%"


def _when(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M")
