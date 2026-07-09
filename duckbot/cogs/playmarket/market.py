import math
from decimal import ROUND_DOWN, Decimal
from typing import List, Literal, Optional

from discord import Color, Embed, Interaction
from discord.app_commands import Choice
from discord.ext import commands, tasks
from sqlalchemy import String, cast, or_

from duckbot.db import Database
from duckbot.util.datetime import now
from duckbot.util.users import get_user

from . import config, lmsr
from .models import LedgerEntry, Market, PlayerAccount, Position, Season, SeasonResult

CENT = Decimal("0.000001")

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


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
        async with context.typing():
            await self.list_markets(context, status)

    # --- economy commands -------------------------------------------------

    @market_group.command(name="balance", description="Show your coin balance and active bets.")
    async def balance_command(self, context: commands.Context):
        async with context.typing():
            await self.balance(context)

    async def balance(self, context: commands.Context):
        with self.db.session(Season) as session:
            season = self.active_season(session)
            account = self.account(session, season.id, context.author.id)
            rows = session.query(Position, Market).join(Market, Position.market_id == Market.id).filter(Position.user_id == account.id, Market.status == "OPEN").order_by(Market.id.desc()).all()
            session.commit()
            lines = [f"**{await self._name(context, account.id)}** — {_coins(account.balance)} coins"]
            lines += [f"**{m.id}** {m.question} — YES {_pct(self._price(m))} · you hold {_coins(p.yes_shares)} YES / {_coins(p.no_shares)} NO" for p, m in rows if p.yes_shares or p.no_shares]
        await context.send("\n".join(lines))

    @market_group.command(name="claim", description="Get a coin top-up when you're low and have no active bets.")
    async def claim_command(self, context: commands.Context):
        async with context.typing():
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

    @market_group.command(name="leaderboard", description="See who's winning this season.")
    async def leaderboard_command(self, context: commands.Context):
        async with context.typing():
            await self.leaderboard(context)

    async def leaderboard(self, context: commands.Context):
        with self.db.session(Season) as session:
            standings = self._standings(session)
            session.commit()
        if not standings:
            return await context.send("Nobody's played yet. Buncha cowards.")
        await context.send(embed=await self._leaderboard_embed(context, standings))

    # --- market commands --------------------------------------------------

    @market_group.command(name="list", description="Browse markets and their current YES odds.")
    async def list_command(self, context: commands.Context, status: Optional[str] = None):
        async with context.typing():
            await self.list_markets(context, status)

    async def list_markets(self, context: commands.Context, status: Optional[str]):
        with self.db.session(Market) as session:
            query = session.query(Market).filter(Market.status == (status.upper() if status else "OPEN"))
            markets = query.order_by(Market.id.desc()).all()
            if not markets:
                return await context.send("No markets. What, you hate fun?")
            embed = Embed(title=f"{(status or 'open').title()} Markets", color=Color.blurple())
            for market in markets:
                value = "\n".join([f"YES {_pct(self._price(market))}"] + await self._holders(context, session, market))
                embed.add_field(name=f"Market {market.id} — {market.question}", value=value, inline=False)
        await context.send(embed=embed)

    @market_group.command(name="create", description="Open a new question for people to bet on.")
    async def create_command(self, context: commands.Context, question: str, liquidity: Literal["low", "med", "high"] = "med"):
        async with context.typing():
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

    @market_group.command(name="bet", description="Bet coins on a market resolving YES or NO.")
    async def bet_command(self, context: commands.Context, market: int, side: Literal["yes", "no"], amount: int):
        async with context.typing():
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
            action = f"{context.author.display_name} bought {_coins(shares)} {side.upper()} shares for {_coins(cost)} coins."
            await context.send(embed=await self._trade_embed(context, session, market, action, side))

    @market_group.command(name="sell", description="Cash out some or all of your position in a market.")
    async def sell_command(self, context: commands.Context, market: int, side: Literal["yes", "no"], shares: str):
        async with context.typing():
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
            action = f"{context.author.display_name} sold {_coins(amount)} {side.upper()} shares for {_coins(proceeds)} coins."
            await context.send(embed=await self._trade_embed(context, session, market, action, side))

    @market_group.command(name="resolve", description="Close your market with an outcome and pay out winners.")
    async def resolve_command(self, context: commands.Context, market: int, outcome: Literal["yes", "no", "void"]):
        async with context.typing():
            await self.resolve(context, market, outcome)

    async def resolve(self, context: commands.Context, market_id: int, outcome: str):
        with self.db.session(Market) as session:
            market = self._lock_market(session, market_id)
            if market is None:
                return await context.send("No such market, brother.")
            if market.status == "RESOLVED" and outcome == "void":
                return await self.void_resolved(context, session, market)
            if market.status != "OPEN":
                return await context.send("That one's already in the books, brother.")
            if context.author.id != market.creator_id and not await self._is_admin(context):
                return await context.send("Not your market, not your call.")
            results = []
            for pos in session.query(Position).filter_by(market_id=market.id).all():
                if not pos.yes_shares and not pos.no_shares:
                    continue
                invested = self._invested(session, pos.user_id, market.id)
                results.append((pos.user_id, pos.yes_shares, pos.no_shares, invested, self._payout(pos, outcome, invested)))
            self._resolve_market(session, market, outcome)
            session.commit()
            mentions = " ".join([await self._name(context, r[0], mention=True) for r in results])
            await context.send(mentions or None, embed=await self._resolve_embed(context, market, outcome, results))

    async def void_resolved(self, context: commands.Context, session, market):
        """Admin correction: reverse a bad resolution, clawing back payouts and refunding stakes."""
        if not await self._is_admin(context):
            return await context.send("Reversing a resolution is above your pay grade, brother.")
        if session.get(Season, market.season_id).status == "archived":
            return await context.send("That season's ancient history, brother.")
        results = self._void_resolved(session, market)
        session.commit()
        mentions = " ".join([await self._name(context, r[0], mention=True) for r in results])
        await context.send(mentions or None, embed=await self._void_resolved_embed(context, market, results))

    def _void_resolved(self, session, market):
        """Positions are gone post-resolution; rebuild each user's stake and payout from the ledger."""
        results = []
        user_ids = [uid for (uid,) in session.query(LedgerEntry.user_id).filter_by(market_id=market.id).distinct().all()]
        for user_id in user_ids:
            clawback = sum(e.delta for e in session.query(LedgerEntry).filter_by(user_id=user_id, market_id=market.id, reason="payout").all())
            refund = max(0, -self._invested(session, user_id, market.id))
            if refund - clawback != 0:
                self._credit(session, market.season_id, self._lock_account(session, user_id), market.id, refund - clawback, "void")
            if clawback or refund:
                results.append((user_id, clawback, refund))
        market.status = "VOID"
        market.outcome = "void"
        return results

    async def _void_resolved_embed(self, context, market, results) -> Embed:
        embed = Embed(title=f"Market {market.id} — {market.question}", description="Resolution reversed — market **VOIDED** by an admin.", color=Color.greyple())
        lines = []
        for user_id, clawback, refund in sorted(results, key=lambda r: r[2] - r[1], reverse=True):
            lines.append(f"{await self._name(context, user_id)} — clawed back {_coins(clawback)}, refunded {_coins(refund)} ({refund - clawback:+,})")
        if lines:
            embed.add_field(name="Corrections", value="\n".join(lines), inline=False)
        return embed

    @market_group.autocomplete("status")
    @list_command.autocomplete("status")
    async def status_autocomplete(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return [Choice(name=s.title(), value=s) for s in ("OPEN", "RESOLVED", "VOID") if current.upper() in s]

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
        """Pay out winning shares (net stake back on void), close positions, finalise."""
        for position in session.query(Position).filter_by(market_id=market.id).all():
            payout = self._payout(position, outcome, self._invested(session, position.user_id, market.id))
            if payout > 0:
                account = self._lock_account(session, position.user_id)
                self._credit(session, market.season_id, account, market.id, payout, "refund" if outcome == "void" else "payout")
            session.delete(position)
        market.status = "VOID" if outcome == "void" else "RESOLVED"
        market.outcome = outcome

    def _invested(self, session, user_id, market_id) -> int:
        """Net of the player's bets and sells on a market; negative while coins are in."""
        return sum(e.delta for e in session.query(LedgerEntry).filter_by(user_id=user_id, market_id=market_id).filter(LedgerEntry.reason.in_(("bet", "sell"))).all())

    def _payout(self, position, outcome, invested) -> int:
        if outcome == "void":
            return max(0, -invested)
        return _whole(position.yes_shares if outcome == "yes" else position.no_shares)

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
        """(user_id, cash, shares_value) ranked by net worth (cash + shares_value) high to low."""
        cash = {a.id: a.balance for a in session.query(PlayerAccount).all()}
        shares_value = {uid: Decimal(0) for uid in cash}
        rows = session.query(Position, Market).join(Market, Position.market_id == Market.id).filter(Market.status == "OPEN").all()
        for position, market in rows:
            yes_price = Decimal(str(self._price(market)))
            shares_value[position.user_id] += position.yes_shares * yes_price + position.no_shares * (1 - yes_price)
        return sorted(((uid, cash[uid], shares_value[uid]) for uid in cash), key=lambda row: row[1] + row[2], reverse=True)

    def _lock_market(self, session, market_id) -> Optional[Market]:
        return session.query(Market).filter_by(id=market_id).with_for_update().first()

    def _lock_account(self, session, user_id) -> Optional[PlayerAccount]:
        return session.query(PlayerAccount).filter_by(id=user_id).with_for_update().first()

    def _price(self, market) -> float:
        return lmsr.price_yes(float(market.q_yes), float(market.q_no), float(market.b))

    async def _holders(self, context, session, market) -> List[str]:
        positions = session.query(Position).filter(Position.market_id == market.id, (Position.yes_shares > 0) | (Position.no_shares > 0)).all()
        positions.sort(key=lambda p: p.yes_shares + p.no_shares, reverse=True)
        return [f"{await self._name(context, p.user_id)} — {_coins(p.yes_shares)} YES / {_coins(p.no_shares)} NO" for p in positions]

    async def _resolve_embed(self, context, market, outcome: str, results) -> Embed:
        color = Color.green() if outcome == "yes" else Color.red() if outcome == "no" else Color.greyple()
        embed = Embed(title=f"Market {market.id} — {market.question}", description=f"Called **{outcome.upper()}**.", color=color)
        lines = []
        for user_id, yes_shares, no_shares, invested, payout in sorted(results, key=lambda r: r[3] + r[4], reverse=True):
            name = await self._name(context, user_id)
            net = payout + invested
            side = "YES" if yes_shares >= no_shares else "NO"
            if net > 0:
                lines.append(f"{name} — {_coins(-invested)} on {side}, won {_coins(payout)} (+{_coins(net)})")
            elif net < 0:
                lines.append(f"{name} — {_coins(-invested)} on {side}, lost {_coins(-net)}")
            else:
                lines.append(f"{name} — {_coins(-invested)} on {side}, refunded")
        if lines:
            embed.add_field(name="Results", value="\n".join(lines), inline=False)
        return embed

    async def _trade_embed(self, context, session, market, action: str, side: str) -> Embed:
        embed = Embed(title=f"Market {market.id} — {market.question}", description=f"{action}\nYES is now {_pct(self._price(market))}.", color=Color.green() if side == "yes" else Color.red())
        holders = await self._holders(context, session, market)
        if holders:
            embed.add_field(name="Holders", value="\n".join(holders), inline=False)
        return embed

    async def _leaderboard_embed(self, context, standings) -> Embed:
        lines = [await self._standing_line(context, i, uid, cash, shares_value) for i, (uid, cash, shares_value) in enumerate(standings, start=1)]
        return Embed(title="Leaderboard", description="\n".join(lines), color=Color.gold())

    async def _standing_line(self, context, rank, uid, cash, shares_value) -> str:
        name = await self._name(context, uid)
        return f"{MEDALS.get(rank, f'{rank}.')} {name} — {_coins(cash + shares_value)} coins ({_coins(cash)} available)"

    async def _is_admin(self, context) -> bool:
        return await context.bot.is_owner(context.author) or context.author.id in config.ADMIN_IDS

    async def _name(self, context, user_id, mention=False) -> str:
        user = await get_user(self.bot, user_id, context.guild)
        return (user.mention if mention else user.display_name) if user else str(user_id)


def _coins(value) -> str:
    return f"{value:,.0f}"


def _pct(probability: float) -> str:
    return f"{probability * 100:.2f}".rstrip("0").rstrip(".") + "%"
