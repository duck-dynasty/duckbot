import math
from unittest import mock

import pytest

from duckbot.cogs.playmarket import config
from duckbot.cogs.playmarket.models import Market, Proposal, Season, SeasonResult
from tests.cogs.playmarket.conftest import (
    account,
    close_markets,
    ledger,
    market_row,
    open_market,
    position,
    reconciles,
    set_balance,
)

BET = 500  # a typical bet, scaled to the integer economy
STARTING = config.STARTING_BALANCE


def reasons(db, user_id):
    return [e.reason for e in ledger(db, user_id)]


# --- account & season bootstrap -----------------------------------------


async def test_first_interaction_grants_the_starting_balance(cog, alice, db):
    await cog.balance(alice)
    assert account(db, 1).balance == STARTING


async def test_first_interaction_writes_a_season_grant(cog, alice, db):
    await cog.balance(alice)
    assert reasons(db, 1) == ["season_grant"]


async def test_first_interaction_creates_season_one(cog, alice, db):
    await cog.balance(alice)
    with db.session(Season) as session:
        seasons = session.query(Season).all()
    assert len(seasons) == 1 and seasons[0].name == "Season 1"


async def test_balance_reports_coins(cog, alice):
    await cog.balance(alice)
    assert "10,000 coins" in alice.send.call_args.args[0]


async def test_balance_lists_open_positions(cog, alice, db):
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


async def test_create_opens_a_market_at_fifty_percent(cog, alice, db):
    market_id = await open_market(cog, alice)
    market = market_row(db, market_id)
    assert market.status == "OPEN" and market.q_yes == 0 and market.q_no == 0


async def test_create_announces_the_new_market(cog, alice):
    await cog.create(alice, "Rain?", "NWS call", "in 1 day", "med")
    assert "YES 50%" in alice.send.call_args.args[0]


@pytest.mark.parametrize("tier,b", [("low", 500), ("med", 1000), ("high", 2000)])
async def test_create_sets_liquidity_and_subsidy_by_tier(cog, alice, db, tier, b):
    market_id = await open_market(cog, alice, liquidity=tier)
    market = market_row(db, market_id)
    assert market.b == b
    assert market.subsidy == math.floor(b * math.log(2))


async def test_create_rejects_an_unparseable_close_time(cog, alice, db):
    await cog.create(alice, "Q", "rules", "whenever", "med")
    assert "can't read that close time" in alice.send.call_args.args[0]
    with db.session(Market) as session:
        assert session.query(Market).count() == 0


async def test_create_rejects_a_close_time_in_the_past(cog, alice, clock):
    await cog.create(alice, "Q", "rules", "2020-01-01", "med")
    assert alice.send.call_args.args[0] == "The close time must be in the future."


async def test_create_rejects_a_close_after_the_season_ends(cog, alice):
    await cog.create(alice, "Q", "rules", "in 400 days", "med")
    assert "before the season ends" in alice.send.call_args.args[0]


async def test_create_is_blocked_once_the_season_is_settling(cog, alice, clock):
    await open_market(cog, alice)  # creates Season 1
    clock.advance(days=183)  # past the season end
    await cog.create(alice, "Q", "rules", "in 1 day", "med")
    assert alice.send.call_args.args[0] == "The season is wrapping up; no new markets right now."


# --- bet -----------------------------------------------------------------


async def test_bet_buys_yes_shares_and_moves_the_price(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "Bought 832 YES shares for 500 coins. YES is now 70%."


async def test_bet_records_the_position(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert float(position(db, 1, market_id).yes_shares) == pytest.approx(831.8, abs=1)


async def test_bet_debits_exactly_the_budget(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert account(db, 1).balance == STARTING - BET


async def test_bet_writes_a_bet_ledger_row(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    assert reasons(db, 1) == ["season_grant", "bet"]


async def test_bet_on_no_lowers_the_yes_price(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "no", BET)
    assert float(market_row(db, market_id).q_no) > 0
    assert cog._price(market_row(db, market_id)) < 0.5


async def test_bet_below_the_minimum_is_rejected(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 5)
    assert alice.send.call_args.args[0] == "Minimum bet is 10 coins."
    assert market_row(db, market_id).q_yes == 0


async def test_bet_more_than_you_can_afford_is_rejected(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", STARTING * 100)
    assert alice.send.call_args.args[0] == "You only have 10,000 coins."
    assert account(db, 1).balance == STARTING


async def test_bet_on_a_closed_market_is_rejected(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.bet(alice, market_id, "yes", BET)
    assert "closed for trading" in alice.send.call_args.args[0]


async def test_bet_keeps_the_ledger_reconciled(cog, alice, bob, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", 750)
    assert reconciles(db)


# --- quote ---------------------------------------------------------------


async def test_quote_does_not_change_the_market(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.quote(alice, market_id, "yes", BET)
    assert market_row(db, market_id).q_yes == 0


async def test_quote_does_not_create_an_account(cog, alice, bob, db):
    market_id = await open_market(cog, alice)
    await cog.quote(bob, market_id, "yes", BET)
    assert account(db, 2) is None


async def test_quote_reports_shares_and_resulting_price(cog, alice):
    market_id = await open_market(cog, alice)
    await cog.quote(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "500 coins buys ~832 YES shares; YES would move to 70%."


async def test_quote_on_a_closed_market_is_rejected(cog, alice, clock):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.quote(alice, market_id, "yes", BET)
    assert alice.send.call_args.args[0] == "That market is not open for trading."


# --- sell ----------------------------------------------------------------


async def test_sell_all_clears_the_position(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert position(db, 1, market_id).yes_shares == 0


async def test_sell_returns_almost_the_whole_stake(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    # Round-trip costs only the house's rounding edge, so the balance lands just below the start.
    assert float(account(db, 1).balance) == pytest.approx(STARTING, abs=2)
    assert account(db, 1).balance <= STARTING


async def test_sell_reduces_the_market_quantity(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "200")
    assert float(market_row(db, market_id).q_yes) == pytest.approx(631.8, abs=1)


async def test_sell_more_than_held_is_rejected(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.sell(alice, market_id, "yes", "10")
    assert alice.send.call_args.args[0] == "You hold 0 YES shares."


async def test_sell_writes_a_sell_ledger_row(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert reasons(db, 1) == ["season_grant", "bet", "sell"]


async def test_sell_on_a_closed_market_is_rejected(cog, alice, clock):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await close_markets(cog, clock)
    await cog.sell(alice, market_id, "yes", "all")
    assert alice.send.call_args.args[0] == "Trading is closed on that market."


async def test_sell_keeps_the_ledger_reconciled(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.sell(alice, market_id, "yes", "all")
    assert reconciles(db)


# --- propose -------------------------------------------------------------


async def test_propose_moves_a_closed_market_to_proposed(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    assert market_row(db, market_id).status == "PROPOSED"


async def test_propose_holds_the_bond(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    assert (account(db, 2).balance, account(db, 2).locked) == (STARTING - config.PROPOSE_BOND, config.PROPOSE_BOND)


async def test_propose_opens_a_24h_dispute_window(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    with db.session(Proposal) as session:
        proposal = session.query(Proposal).filter_by(market_id=market_id).one()
    assert proposal.window_ends == clock.t + config.DISPUTE_WINDOW


async def test_propose_before_close_is_rejected(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.propose(alice, market_id, "yes")
    assert alice.send.call_args.args[0] == "Only a closed, unresolved market can be proposed."


async def test_propose_without_enough_for_the_bond_is_rejected(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.balance(bob)  # create bob's account
    set_balance(db, 2, 10)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    assert bob.send.call_args.args[0] == "You need 500 coins for the bond."


# --- dispute -------------------------------------------------------------


async def test_dispute_moves_the_market_to_disputed(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    assert market_row(db, market_id).status == "DISPUTED"


async def test_dispute_holds_a_matching_bond(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    assert account(db, 3).locked == config.DISPUTE_BOND


async def test_disputing_your_own_proposal_is_rejected(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(bob, market_id)
    assert bob.send.call_args.args[0] == "You can't dispute your own proposal."


async def test_disputing_with_no_proposal_is_rejected(cog, alice, clock):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.dispute(alice, market_id)
    assert alice.send.call_args.args[0] == "There is no open proposal to dispute."


async def test_disputing_after_the_window_finalizes_the_market(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    clock.advance(hours=25)
    await cog.dispute(carol, market_id)
    assert "dispute window has closed" in carol.send.call_args.args[0]
    assert market_row(db, market_id).status == "RESOLVED"


# --- resolve -------------------------------------------------------------


async def test_admin_can_resolve_a_closed_market_directly(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.resolve(alice, market_id, "yes")
    assert market_row(db, market_id).status == "RESOLVED"


async def test_resolving_yes_pays_the_yes_holders(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", BET)
    await close_markets(cog, clock)
    await cog.resolve(alice, market_id, "yes")
    assert account(db, 1).balance > STARTING  # winning YES paid out above the stake
    assert account(db, 2).balance == STARTING - BET  # losing NO got nothing


async def test_resolving_void_pays_half_to_everyone(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 300)
    await close_markets(cog, clock)
    await cog.resolve(alice, market_id, "void")
    market = market_row(db, market_id)
    assert market.status == "VOID"
    # 300 coins buys ~530 YES shares at b=1000; each redeems at 0.5 -> ~265 back on the 9,700 remaining.
    assert float(account(db, 1).balance) == pytest.approx(9965, abs=1)


async def test_resolving_clears_all_positions(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await close_markets(cog, clock)
    await cog.resolve(alice, market_id, "yes")
    assert position(db, 1, market_id) is None


async def test_resolving_before_close_is_rejected(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.resolve(alice, market_id, "yes")
    assert alice.send.call_args.args[0] == "That market can't be resolved until it closes."
    assert market_row(db, market_id).status == "OPEN"


async def test_resolve_returns_the_bond_on_an_undisputed_proposal(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")  # proposed, nobody disputes
    await cog.resolve(alice, market_id, "yes")  # admin settles it directly
    assert account(db, 2).balance == STARTING and account(db, 2).locked == 0
    assert market_row(db, market_id).status == "RESOLVED"


async def test_resolve_awards_the_disputed_bond_to_a_correct_proposer(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    await cog.resolve(alice, market_id, "yes")  # proposer was right
    assert account(db, 2).balance == STARTING + config.DISPUTE_BOND  # bond back + the disputer's bond
    assert account(db, 3).balance == STARTING - config.DISPUTE_BOND  # forfeited the dispute bond


async def test_resolve_awards_the_disputed_bond_to_a_correct_disputer(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    await cog.resolve(alice, market_id, "no")  # disputer was right
    assert account(db, 3).balance == STARTING + config.PROPOSE_BOND
    assert account(db, 2).balance == STARTING - config.PROPOSE_BOND


async def test_resolving_void_returns_both_bonds(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    await cog.resolve(alice, market_id, "void")
    assert account(db, 2).balance == STARTING and account(db, 2).locked == 0
    assert account(db, 3).balance == STARTING and account(db, 3).locked == 0


async def test_resolving_keeps_the_ledger_reconciled(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", BET)
    await close_markets(cog, clock)
    await cog.propose(alice, market_id, "yes")
    await cog.dispute(carol, market_id)
    await cog.resolve(bob, market_id, "yes")
    assert reconciles(db)


# --- scheduler / state machine ------------------------------------------


async def test_tick_closes_a_market_whose_time_has_passed(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    clock.advance(days=2)
    await cog.tick()
    assert market_row(db, market_id).status == "CLOSED"


async def test_tick_finalizes_a_proposal_after_its_window(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    clock.advance(hours=25)
    await cog.tick()
    assert market_row(db, market_id).status == "RESOLVED"
    assert account(db, 2).locked == 0  # proposer's bond returned


async def test_tick_leaves_a_disputed_market_for_an_admin(cog, alice, bob, carol, clock, db):
    market_id = await open_market(cog, alice)
    await close_markets(cog, clock)
    await cog.propose(bob, market_id, "yes")
    await cog.dispute(carol, market_id)
    clock.advance(days=5)
    await cog.tick()
    assert market_row(db, market_id).status == "DISPUTED"


async def test_tick_closes_several_markets_at_once(cog, alice, clock, db):
    first = await open_market(cog, alice)
    second = await open_market(cog, alice)
    clock.advance(days=2)
    await cog.tick()
    assert market_row(db, first).status == "CLOSED" and market_row(db, second).status == "CLOSED"


# --- claim (need-based top-up) ------------------------------------------


async def test_claim_tops_a_broke_player_up_to_the_target(cog, alice, db):
    await cog.balance(alice)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    assert account(db, 1).balance == config.TOPUP_TARGET


async def test_claim_is_rejected_when_not_broke(cog, alice, db):
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "You only qualify when your balance is under 1,000."


async def test_claim_is_rejected_with_open_positions(cog, alice, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "Sell or resolve your open positions before claiming."


async def test_claim_is_rejected_within_the_cooldown(cog, alice, db):
    await cog.balance(alice)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    assert alice.send.call_args.args[0] == "You already claimed this week."


async def test_claim_is_allowed_again_after_the_cooldown(cog, alice, clock, db):
    await cog.balance(alice)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    clock.advance(days=8)
    set_balance(db, 1, 10)
    await cog.claim(alice)
    assert account(db, 1).balance == config.TOPUP_TARGET


# --- leaderboard & season -----------------------------------------------


async def test_leaderboard_is_empty_before_anyone_plays(cog, alice):
    await cog.leaderboard(alice)
    assert alice.send.call_args.args[0] == "Nobody has played yet."


async def test_leaderboard_ranks_by_net_worth(cog, alice, bob, db):
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


async def test_rollover_archives_the_season_and_starts_the_next(cog, alice, clock, db):
    await open_market(cog, alice)
    clock.advance(days=190)  # past the season end plus the 7-day grace
    await cog.tick()
    with db.session(Season) as session:
        statuses = {s.name: s.status for s in session.query(Season).all()}
    assert statuses == {"Season 1": "archived", "Season 2": "active"}


async def test_rollover_resets_every_balance(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.balance(bob)
    clock.advance(days=190)
    await cog.tick()
    assert account(db, 1).balance == STARTING and account(db, 1).locked == 0
    assert account(db, 2).balance == STARTING


async def test_rollover_force_voids_unsettled_markets(cog, alice, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    clock.advance(days=190)
    await cog.tick()
    assert market_row(db, market_id).status == "VOID"


async def test_rollover_records_the_final_standings(cog, alice, bob, clock, db):
    await cog.balance(alice)
    await cog.balance(bob)
    clock.advance(days=190)
    await cog.tick()
    with db.session(Season) as session:
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


async def test_full_dispute_lifecycle_settles_correctly(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", BET)
    await cog.bet(bob, market_id, "no", BET)
    await close_markets(cog, clock)
    await cog.propose(alice, market_id, "yes")
    await cog.dispute(bob, market_id)
    await cog.resolve(alice, market_id, "yes")  # alice (proposer + YES holder) is right
    assert account(db, 1).balance > STARTING + config.DISPUTE_BOND  # payout + bond back + won dispute bond
    assert account(db, 2).balance == STARTING - BET - config.DISPUTE_BOND  # lost bet + lost dispute bond
    assert account(db, 1).locked == 0 and account(db, 2).locked == 0
    assert reconciles(db)


async def test_coins_stay_whole_after_payouts(cog, alice, bob, clock, db):
    market_id = await open_market(cog, alice)
    await cog.bet(alice, market_id, "yes", 333)
    await cog.bet(bob, market_id, "no", 777)
    await close_markets(cog, clock)
    await cog.resolve(alice, market_id, "yes")
    for uid in (1, 2):
        assert isinstance(account(db, uid).balance, int)
