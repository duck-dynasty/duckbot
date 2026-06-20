import math
from unittest import mock

import pytest

from duckbot.cogs.playmarket import config
from duckbot.cogs.playmarket.models import Season, SeasonResult
from tests.cogs.playmarket.conftest import (
    account,
    ledger,
    make_context,
    market_row,
    open_market,
    position,
    reconciles,
    set_balance,
)

BET = 500
STARTING = config.STARTING_BALANCE


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


async def test_balance_lists_open_positions(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.balance(alice)
    assert f"market {market_id}" in alice.send.call_args.args[0]


# --- list & show ---------------------------------------------------------


async def test_list_says_so_when_there_are_no_markets(cog, alice):
    await cog.list_markets(alice, None)
    assert alice.send.call_args.args[0] == "No markets. Start one with `/market create`."


async def test_list_shows_open_markets_with_their_price(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.list_markets(alice, None)
    assert f"**{market_id}**" in alice.send.call_args.args[0] and "YES 50%" in alice.send.call_args.args[0]


async def test_show_reports_the_question_and_rules(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.show(alice, market_id)
    assert "official ruling" in alice.send.call_args.args[0]


async def test_show_includes_your_position(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.show(alice, market_id)
    assert "You hold 832 YES" in alice.send.call_args.args[0]


async def test_show_rejects_an_unknown_market(cog, alice):
    await cog.show(alice, 999)
    assert alice.send.call_args.args[0] == "No such market."


# --- create --------------------------------------------------------------


async def test_create_opens_a_market_at_fifty_percent(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    market = market_row(in_memory_db, market_id)
    assert market.status == "OPEN" and market.q_yes == 0 and market.q_no == 0


async def test_create_announces_the_new_market(cog, alice):
    await cog.create(alice, "Rain?", "NWS call", "med")
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
    await cog.create(alice, "Q", "rules", "med")
    assert alice.send.call_args.args[0] == "The season is wrapping up; no new markets right now."


# --- bet -----------------------------------------------------------------


async def test_bet_buys_yes_shares_and_moves_the_price(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "Bought 832 YES shares for 500 coins. YES is now 70%."


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


async def test_bet_below_the_minimum_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 5)
    assert alice.send.call_args.args[0] == "Minimum bet is 10 coins."
    assert market_row(in_memory_db, market_id).q_yes == 0


async def test_bet_more_than_you_can_afford_is_rejected(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", STARTING * 100)
    assert alice.send.call_args.args[0] == "You only have 10,000 coins."
    assert account(in_memory_db, 1).balance == STARTING


async def test_bet_on_a_resolved_market_is_rejected(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    await cog.bet(bob, market_id, "yes", BET)
    assert "trading is closed" in bob.send.call_args.args[0]


async def test_bet_keeps_the_ledger_reconciled(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", 750)
    assert reconciles(in_memory_db)


# --- quote ---------------------------------------------------------------


async def test_quote_does_not_change_the_market(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.quote(alice, market_id, "yes", BET)
    assert market_row(in_memory_db, market_id).q_yes == 0


async def test_quote_does_not_create_an_account(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.quote(bob, market_id, "yes", BET)
    assert account(in_memory_db, 2) is None


async def test_quote_reports_shares_and_resulting_price(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.quote(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "500 coins buys ~832 YES shares; YES would move to 70%."


async def test_quote_on_a_resolved_market_is_rejected(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    await cog.quote(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "That market is not open for trading."


# --- sell ----------------------------------------------------------------


async def test_sell_all_clears_the_position(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert position(in_memory_db, 1, market_id).yes_shares == 0


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
    assert alice.send.call_args.args[0] == "You hold 0 YES shares."


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
    assert "trading is closed" in alice.send.call_args.args[0]


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
    assert alice.send.call_args.args[0] == f"Market {market_id} resolved **YES**. Payouts done."


async def test_a_non_creator_non_admin_cannot_resolve(cog, alice, bob, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.resolve(bob, market_id, "yes")
    assert bob.send.call_args.args[0] == "Only the market's creator or an admin can resolve it."
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
    assert alice.send.call_args.args[0] == "That market is already resolved."


async def test_resolving_an_unknown_market_is_rejected(cog, alice):
    await cog.resolve(alice, 999, "yes")
    assert alice.send.call_args.args[0] == "No such market."


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
    assert alice.send.call_args.args[0] == "You only qualify when your balance is under 1,000."


async def test_claim_is_rejected_with_open_positions(cog, alice, in_memory_db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "Sell or resolve your open positions before claiming."


async def test_claim_is_rejected_within_the_cooldown(cog, alice, in_memory_db):
    await cog.balance(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "You already claimed this week."


async def test_claim_is_allowed_again_after_the_cooldown(cog, alice, clock, in_memory_db):
    await cog.balance(alice)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    clock.advance(days=8)
    set_balance(in_memory_db, 1, 10)
    await cog.claim(alice)
    assert account(in_memory_db, 1).balance == config.TOPUP_TARGET


# --- leaderboard & season -----------------------------------------------


async def test_leaderboard_is_empty_before_anyone_plays(cog, alice):
    await cog.leaderboard(alice)
    assert alice.send.call_args.args[0] == "Nobody has played yet."


async def test_leaderboard_ranks_by_net_worth(cog, alice, bob, in_memory_db):
    await cog.balance(alice)  # alice sits on the starting balance
    market_id = await open_market(cog, bob)
    await cog.bet(bob, market_id, "yes", BET)  # bob's position is worth more than his spent coins
    await cog.leaderboard(alice)
    message = alice.send.call_args.args[0]
    assert message.index("user2") < message.index("user1")


async def test_season_reports_the_name_and_time_left(cog, alice):
    await cog.season(alice)
    assert "Season 1" in alice.send.call_args.args[0] and "days left" in alice.send.call_args.args[0]


async def test_season_reports_when_it_is_settling(cog, alice, clock):
    await open_market(cog, alice)
    clock.advance(days=183)
    await cog.season(alice)
    assert "ending soon" in alice.send.call_args.args[0]


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


# --- cog lifecycle -------------------------------------------------------


def test_cog_unload_cancels_the_loop(cog):
    cog.tick_loop = mock.Mock()
    cog.cog_unload()
    cog.tick_loop.cancel.assert_called_once()


async def test_before_tick_waits_for_the_bot_to_be_ready(cog):
    await cog.before_tick()
    cog.bot.wait_until_ready.assert_called_once()


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
