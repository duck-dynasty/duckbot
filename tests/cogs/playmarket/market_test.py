import datetime
import math
from unittest import mock

import discord
import pytest

from duckbot.cogs.playmarket import config
from duckbot.cogs.playmarket.market import PlayMarket
from duckbot.cogs.playmarket.models import (
    LedgerEntry,
    Market,
    PlayerAccount,
    Position,
    Season,
    SeasonResult,
)

BET = 500
STARTING = config.STARTING_BALANCE


class Clock:
    """A movable replacement for now()."""

    def __init__(self):
        self.t = datetime.datetime(2024, 1, 1, 12, 0)

    def __call__(self):
        return self.t

    def advance(self, **kwargs):
        self.t += datetime.timedelta(**kwargs)
        return self.t


@pytest.fixture
def clock():
    movable = Clock()
    with mock.patch("duckbot.cogs.playmarket.market.now", side_effect=movable):
        yield movable


@pytest.fixture
def cog(bot, in_memory_db, clock):
    market = PlayMarket(bot, in_memory_db)
    market.tick_loop.cancel()  # don't run the loop mid-test
    return market


def make_context(user_id):
    ctx = mock.Mock()
    ctx.author = mock.Mock(id=user_id, display_name=f"user{user_id}")
    ctx.guild.get_member = lambda uid: mock.Mock(id=uid, display_name=f"user{uid}")
    ctx.send = mock.AsyncMock()
    ctx.bot.is_owner = mock.AsyncMock(return_value=False)
    return ctx


@pytest.fixture
def alice():
    return make_context(1)


@pytest.fixture
def bob():
    return make_context(2)


@pytest.fixture
def carol():
    return make_context(3)


def account(in_memory_db, user_id):
    with in_memory_db.session(PlayerAccount) as session:
        return session.get(PlayerAccount, user_id)


def market_row(in_memory_db, market_id):
    with in_memory_db.session(Market) as session:
        return session.get(Market, market_id)


def position(in_memory_db, user_id, market_id):
    with in_memory_db.session(Position) as session:
        return session.get(Position, (user_id, market_id))


def ledger(in_memory_db, user_id):
    with in_memory_db.session(LedgerEntry) as session:
        return session.query(LedgerEntry).filter_by(user_id=user_id).all()


def reconciles(in_memory_db):
    """Each player's balance equals their ledger sum."""
    with in_memory_db.session(PlayerAccount) as session:
        for player in session.query(PlayerAccount).all():
            total = sum((e.delta for e in session.query(LedgerEntry).filter_by(user_id=player.id).all()), 0)
            if player.balance != total:
                return False
    return True


def set_balance(in_memory_db, user_id, amount):
    with in_memory_db.session(PlayerAccount) as session:
        session.get(PlayerAccount, user_id).balance = int(amount)
        session.commit()


async def open_market(cog, ctx, liquidity="med"):
    """Create a market and return its id."""
    await cog.create(ctx, "Will it happen?", liquidity)
    with cog.db.session(Market) as session:
        return session.query(Market).order_by(Market.id.desc()).first().id


def reasons(in_memory_db, user_id):
    return [e.reason for e in ledger(in_memory_db, user_id)]


# --- account & season bootstrap -----------------------------------------


async def test_first_interaction_grants_the_starting_balance(cog, alice, in_memory_db):
    await cog.balance(alice)
    assert account(in_memory_db, 1).balance == STARTING


async def test_first_interaction_writes_a_season_grant(cog, alice, in_memory_db):
    await cog.balance(alice)
    assert reasons(in_memory_db, 1) == ["season_grant"]


async def test_first_interaction_creates_season_one(cog, alice, in_memory_db):
    await cog.balance(alice)
    with in_memory_db.session(Season) as session:
        seasons = session.query(Season).all()
    assert len(seasons) == 1 and seasons[0].name == "Season 1"


async def test_balance_reports_coins(cog, alice):
    await cog.balance(alice)
    assert "10,000 coins" in alice.send.call_args.args[0]


async def test_balance_lists_your_open_bets(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.balance(alice)
    message = alice.send.call_args.args[0]
    assert f"**{market_id}**" in message and "832 YES" in message


async def test_balance_omits_resolved_bets(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.resolve(alice, market_id, "yes")
    await cog.balance(alice)
    assert f"**{market_id}**" not in alice.send.call_args.args[0]


# --- list ----------------------------------------------------------------


async def test_list_says_so_when_there_are_no_markets(cog, alice):
    await cog.list_markets(alice, None)
    assert alice.send.call_args.args[0] == "No markets. What, you hate fun?"


async def test_list_shows_open_markets_with_their_price(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.list_markets(alice, None)
    assert f"**{market_id}**" in alice.send.call_args.args[0] and "YES 50%" in alice.send.call_args.args[0]


# --- create --------------------------------------------------------------


async def test_create_opens_a_market_at_fifty_percent(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    market = market_row(in_memory_db, market_id)
    assert market.status == "OPEN" and market.q_yes == 0 and market.q_no == 0


async def test_create_announces_the_new_market(cog, alice):
    await cog.create(alice, "Rain?", "med")
    assert "YES 50%" in alice.send.call_args.args[0]


@pytest.mark.parametrize("tier,b", [("low", 500), ("med", 1000), ("high", 2000)])
async def test_create_sets_liquidity_and_subsidy_by_tier(cog, alice, in_memory_db, tier, b):
    market_id = await open_market(cog, alice, liquidity=tier)
    market = market_row(in_memory_db, market_id)
    assert market.b == b
    assert market.subsidy == math.floor(b * math.log(2))


async def test_create_is_blocked_once_the_season_is_settling(cog, alice, clock):
    await open_market(cog, alice)  # creates Season 1
    clock.advance(days=183)  # past the season end
    await cog.create(alice, "Q", "med")
    assert alice.send.call_args.args[0] == "Season's wrapping up, no new markets. Pump the brakes."


# --- bet -----------------------------------------------------------------


async def test_bet_buys_yes_shares_and_moves_the_price(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="user1 bought 832 YES shares for 500 coins.\nYES is now 69.67%.", color=discord.Color.green())
    expected.add_field(name="Holders", value="user1 — 832 YES / 0 NO", inline=False)
    alice.send.assert_called_with(embed=expected)


async def test_bet_embed_lists_every_holder(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", BET)
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="user2 bought 1,144 NO shares for 500 coins.\nYES is now 42.26%.", color=discord.Color.red())
    expected.add_field(name="Holders", value="user2 — 0 YES / 1,144 NO\nuser1 — 832 YES / 0 NO", inline=False)
    bob.send.assert_called_with(embed=expected)


async def test_bet_records_the_position(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert float(position(in_memory_db, 1, market_id).yes_shares) == pytest.approx(831.8, abs=1)


async def test_bet_debits_exactly_the_budget(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert account(in_memory_db, 1).balance == STARTING - BET


async def test_bet_writes_a_bet_ledger_row(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert reasons(in_memory_db, 1) == ["season_grant", "bet"]


async def test_bet_on_no_lowers_the_yes_price(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "no", BET)
    assert float(market_row(in_memory_db, market_id).q_no) > 0
    assert cog._price(market_row(in_memory_db, market_id)) < 0.5
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="user1 bought 832 NO shares for 500 coins.\nYES is now 30.33%.", color=discord.Color.red())
    expected.add_field(name="Holders", value="user1 — 0 YES / 832 NO", inline=False)
    alice.send.assert_called_with(embed=expected)


async def test_bet_below_the_minimum_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 5)
    assert alice.send.call_args.args[0] == "10 coins minimum, you cheapskate."
    assert market_row(in_memory_db, market_id).q_yes == 0


async def test_bet_more_than_you_can_afford_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", STARTING * 100)
    assert alice.send.call_args.args[0] == "Broke boy. You've only got 10,000 coins."
    assert account(in_memory_db, 1).balance == STARTING


async def test_bet_on_a_resolved_market_is_rejected(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    await cog.bet(bob, market_id, "yes", BET)
    assert "Ship's sailed" in bob.send.call_args.args[0]


async def test_bet_on_a_missing_market_is_rejected(cog, alice):
    await cog.bet(alice, 999, "yes", BET)
    assert alice.send.call_args.args[0] == "No such market, brother."


async def test_bet_keeps_the_ledger_reconciled(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", 750)
    assert reconciles(in_memory_db)


# --- sell ----------------------------------------------------------------


async def test_sell_all_clears_the_position(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert position(in_memory_db, 1, market_id).yes_shares == 0
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="user1 sold 832 YES shares for 499 coins.\nYES is now 50%.", color=discord.Color.green())
    alice.send.assert_called_with(embed=expected)


async def test_sell_returns_almost_the_whole_stake(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert float(account(in_memory_db, 1).balance) == pytest.approx(STARTING, abs=2)
    assert account(in_memory_db, 1).balance <= STARTING


async def test_sell_reduces_the_market_quantity(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "200")
    assert float(market_row(in_memory_db, market_id).q_yes) == pytest.approx(631.8, abs=1)


async def test_sell_more_than_held_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.sell(alice, market_id, "yes", "10")
    assert alice.send.call_args.args[0] == "You've only got 0 YES shares, brother."


async def test_sell_writes_a_sell_ledger_row(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert reasons(in_memory_db, 1) == ["season_grant", "bet", "sell"]


async def test_sell_on_a_resolved_market_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.resolve(alice, market_id, "yes")
    await cog.sell(alice, market_id, "yes", "all")
    assert "Ship's sailed" in alice.send.call_args.args[0]


async def test_sell_on_a_missing_market_is_rejected(cog, alice):
    await cog.sell(alice, 999, "yes", "all")
    assert alice.send.call_args.args[0] == "No such market, brother."


async def test_sell_keeps_the_ledger_reconciled(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert reconciles(in_memory_db)


# --- resolve (creator only) ----------------------------------------------


async def test_creator_can_resolve_their_market(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    assert market_row(in_memory_db, market_id).status == "RESOLVED"
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="Called **YES**.", color=discord.Color.green())
    alice.send.assert_called_with(embed=expected)


async def test_resolve_embed_shows_winners_and_losers(cog, alice, bob, carol, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(bob, market_id, "yes", BET)
    await cog.bet(carol, market_id, "no", BET)
    await cog.resolve(alice, market_id, "yes")
    expected = discord.Embed(title=f"Market {market_id} — Will it happen?", description="Called **YES**.", color=discord.Color.green())
    expected.add_field(name="Results", value="user2 — 500 on YES, won 831 (+331)\nuser3 — 500 on NO, lost 500", inline=False)
    alice.send.assert_called_with(embed=expected)


async def test_a_non_creator_non_admin_cannot_resolve(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.resolve(bob, market_id, "yes")
    assert bob.send.call_args.args[0] == "Not your market, not your call."
    assert market_row(in_memory_db, market_id).status == "OPEN"


async def test_an_admin_can_resolve_any_market(cog, alice, in_memory_db):
    admin = make_context(config.ADMIN_IDS[0])
    market_id = await open_market(cog, alice)
    await cog.resolve(admin, market_id, "yes")
    assert market_row(in_memory_db, market_id).status == "RESOLVED"


async def test_resolving_an_already_resolved_market_is_rejected(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    await cog.resolve(alice, market_id, "no")
    assert alice.send.call_args.args[0] == "That one's already in the books, brother."


async def test_resolving_an_unknown_market_is_rejected(cog, alice):
    await cog.resolve(alice, 999, "yes")
    assert alice.send.call_args.args[0] == "No such market, brother."


async def test_resolving_yes_pays_the_yes_holders(cog, alice, bob, carol, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(bob, market_id, "yes", BET)
    await cog.bet(carol, market_id, "no", BET)
    await cog.resolve(alice, market_id, "yes")
    assert account(in_memory_db, 2).balance > STARTING  # bob held YES and won
    assert account(in_memory_db, 3).balance == STARTING - BET  # carol held NO and got nothing


async def test_resolving_void_pays_half_to_everyone(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(bob, market_id, "yes", 300)
    await cog.resolve(alice, market_id, "void")
    assert market_row(in_memory_db, market_id).status == "VOID"
    # ~530 YES shares, each redeems at 0.5 on void
    assert float(account(in_memory_db, 2).balance) == pytest.approx(9965, abs=1)


async def test_resolving_clears_all_positions(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(bob, market_id, "yes", BET)
    await cog.resolve(alice, market_id, "yes")
    assert position(in_memory_db, 2, market_id) is None


async def test_resolving_keeps_the_ledger_reconciled(cog, alice, bob, carol, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(bob, market_id, "yes", BET)
    await cog.bet(carol, market_id, "no", BET)
    await cog.resolve(alice, market_id, "yes")
    assert reconciles(in_memory_db)


# --- claim (need-based top-up) ------------------------------------------


async def test_claim_tops_a_broke_player_up_to_the_target(cog, alice, in_memory_db):
    await cog.balance(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert account(in_memory_db, 1).balance == config.TOPUP_TARGET


async def test_claim_is_rejected_when_not_broke(cog, alice, in_memory_db):
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "Quit begging, you're not even broke."


async def test_claim_is_rejected_with_open_positions(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "You've got open bets, brother. No charity for gamblers."


async def test_claim_is_rejected_within_the_cooldown(cog, alice, in_memory_db):
    await cog.balance(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "Already milked that cow this week, greedy."


async def test_claim_is_allowed_again_after_the_cooldown(cog, alice, clock, in_memory_db):
    await cog.balance(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    clock.advance(days=8)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert account(in_memory_db, 1).balance == config.TOPUP_TARGET


# --- leaderboard ---------------------------------------------------------


async def test_leaderboard_is_empty_before_anyone_plays(cog, alice):
    await cog.leaderboard(alice)
    assert alice.send.call_args.args[0] == "Nobody's played yet. Buncha cowards."


async def test_leaderboard_ranks_by_net_worth(cog, alice, bob, in_memory_db):
    await cog.balance(alice)  # alice sits on the starting balance
    market_id = await open_market(cog, bob)
    await cog.bet(bob, market_id, "yes", BET)  # bob's position is worth more than his spent coins
    await cog.leaderboard(alice)
    expected = discord.Embed(title="Leaderboard", description="🥇 user2 — 10,080 coins (9,500 cash + 580 shares)\n🥈 user1 — 10,000 coins (10,000 cash + 0 shares)", color=discord.Color.gold())
    alice.send.assert_called_with(embed=expected)


async def test_leaderboard_medals_the_top_three_then_falls_back_to_numbers(cog, alice):
    standings = [(1, 100, 0), (2, 90, 0), (3, 80, 0), (4, 70, 0)]
    embed = await cog._leaderboard_embed(alice, standings)
    assert embed.description.splitlines() == [
        "🥇 user1 — 100 coins (100 cash + 0 shares)",
        "🥈 user2 — 90 coins (90 cash + 0 shares)",
        "🥉 user3 — 80 coins (80 cash + 0 shares)",
        "4. user4 — 70 coins (70 cash + 0 shares)",
    ]


async def test_standings_splits_cash_and_shares_value(cog, bob, in_memory_db):
    market_id = await open_market(cog, bob)
    await cog.bet(bob, market_id, "yes", BET)
    with in_memory_db.session(Season) as session:
        cash, shares_value = next((c, s) for uid, c, s in cog._standings(session) if uid == 2)
    assert cash == STARTING - BET and shares_value > 0


# --- season rollover -----------------------------------------------------


async def test_rollover_archives_the_season_and_starts_the_next(cog, alice, clock, in_memory_db):
    await open_market(cog, alice)
    clock.advance(days=190)  # past the season end plus the 7-day grace
    await cog.tick()
    with in_memory_db.session(Season) as session:
        statuses = {s.name: s.status for s in session.query(Season).all()}
    assert statuses == {"Season 1": "archived", "Season 2": "active"}


async def test_rollover_resets_every_balance(cog, alice, bob, clock, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.balance(bob)
    clock.advance(days=190)
    await cog.tick()
    assert account(in_memory_db, 1).balance == STARTING
    assert account(in_memory_db, 2).balance == STARTING


async def test_rollover_force_voids_unsettled_markets(cog, alice, clock, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    clock.advance(days=190)
    await cog.tick()
    assert market_row(in_memory_db, market_id).status == "VOID"


async def test_rollover_records_the_final_standings(cog, alice, bob, clock, in_memory_db):
    await cog.balance(alice)
    await cog.balance(bob)
    clock.advance(days=190)
    await cog.tick()
    with in_memory_db.session(Season) as session:
        season_one = session.query(Season).filter_by(name="Season 1").one()
        ranks = {r.rank for r in session.query(SeasonResult).filter_by(season_id=season_one.id).all()}
    assert ranks == {1, 2}


async def test_tick_does_nothing_before_the_season_ends(cog, alice, in_memory_db):
    await cog.balance(alice)  # creates Season 1, still active
    await cog.tick()
    with in_memory_db.session(Season) as session:
        assert session.query(Season).count() == 1  # no rollover yet


# --- market autocomplete -------------------------------------------------


async def test_autocomplete_suggests_open_markets_by_question(cog, alice):
    market_id = await open_market(cog, alice)
    result = await cog.market_autocomplete(mock.Mock(), "happen")
    assert any(c.value == market_id for c in result)


async def test_autocomplete_matches_by_id(cog, alice):
    market_id = await open_market(cog, alice)
    result = await cog.market_autocomplete(mock.Mock(), str(market_id))
    assert [c.value for c in result] == [market_id]


async def test_autocomplete_shows_the_question_in_the_label(cog, alice):
    await open_market(cog, alice)
    result = await cog.market_autocomplete(mock.Mock(), "")
    assert "Will it happen?" in result[0].name


async def test_autocomplete_excludes_resolved_markets(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    result = await cog.market_autocomplete(mock.Mock(), "")
    assert all(c.value != market_id for c in result)


async def test_autocomplete_is_capped_at_25(cog, alice):
    for _ in range(30):
        await open_market(cog, alice)
    result = await cog.market_autocomplete(mock.Mock(), "")
    assert len(result) == 25


async def test_autocomplete_filters_in_the_db_not_after_limiting(cog, alice):
    await cog.create(alice, "UNICORN", "med")  # the oldest market, far past the 25 most-recent
    for _ in range(30):
        await open_market(cog, alice)
    result = await cog.market_autocomplete(mock.Mock(), "unicorn")
    assert any("UNICORN" in c.name for c in result)


# --- status autocomplete -------------------------------------------------


async def test_status_autocomplete_suggests_all_statuses_when_empty(cog):
    result = await cog.status_autocomplete(mock.Mock(), "")
    assert [c.value for c in result] == ["OPEN", "RESOLVED", "VOID"]


async def test_status_autocomplete_filters_by_current(cog):
    result = await cog.status_autocomplete(mock.Mock(), "res")
    assert [c.value for c in result] == ["RESOLVED"]


async def test_status_autocomplete_is_case_insensitive(cog):
    result = await cog.status_autocomplete(mock.Mock(), "VoId")
    assert [c.value for c in result] == ["VOID"]


# --- cog lifecycle & command wiring --------------------------------------


def test_cog_unload_cancels_the_loop(cog):
    cog.tick_loop = mock.Mock()
    cog.cog_unload()
    cog.tick_loop.cancel.assert_called_once()


async def test_before_tick_waits_for_the_bot_to_be_ready(cog):
    await cog.before_tick()
    cog.bot.wait_until_ready.assert_called_once()


async def test_tick_loop_runs_a_tick(cog):
    cog.tick = mock.AsyncMock()
    await PlayMarket.tick_loop.coro(cog)
    cog.tick.assert_awaited_once()


@pytest.mark.parametrize(
    "command,args,delegate",
    [
        ("market_group", (None,), "list_markets"),
        ("balance_command", (), "balance"),
        ("claim_command", (), "claim"),
        ("leaderboard_command", (), "leaderboard"),
        ("list_command", (None,), "list_markets"),
        ("create_command", ("q", "med"), "create"),
        ("bet_command", (7, "yes", 50), "bet"),
        ("sell_command", (7, "yes", "all"), "sell"),
        ("resolve_command", (7, "yes"), "resolve"),
    ],
)
async def test_command_delegates_to_its_method(cog, alice, command, args, delegate):
    setattr(cog, delegate, mock.AsyncMock())
    await getattr(cog, command).callback(cog, alice, *args)
    getattr(cog, delegate).assert_awaited_once_with(alice, *args)


# --- end-to-end integrity -----------------------------------------------


async def test_full_lifecycle_settles_correctly(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", BET)
    await cog.resolve(alice, market_id, "yes")  # alice (creator + YES holder) wins
    assert account(in_memory_db, 1).balance > STARTING
    assert account(in_memory_db, 2).balance == STARTING - BET
    assert reconciles(in_memory_db)


async def test_coins_stay_whole_after_payouts(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 333)
    await cog.bet(bob, market_id, "no", 777)
    await cog.resolve(alice, market_id, "yes")
    for uid in (1, 2):
        assert isinstance(account(in_memory_db, uid).balance, int)
