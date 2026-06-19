import math

import pytest

from duckbot.cogs.playmarket import lmsr


@pytest.mark.parametrize("b", [50.0, 100.0, 200.0])
def test_subsidy_is_b_times_ln2(b):
    assert lmsr.subsidy(b) == pytest.approx(b * math.log(2))


@pytest.mark.parametrize("b", [50.0, 100.0, 200.0])
def test_empty_market_costs_the_subsidy(b):
    assert lmsr.cost(0, 0, b) == pytest.approx(lmsr.subsidy(b))


def test_empty_market_is_a_coin_flip():
    assert lmsr.price_yes(0, 0, 100) == pytest.approx(0.5)


def test_price_is_symmetric():
    assert lmsr.price_yes(40, 90, 100) == pytest.approx(1 - lmsr.price_yes(90, 40, 100))


def test_price_rises_when_yes_is_held():
    assert lmsr.price_yes(83.2, 0, 100) > 0.5


def test_price_falls_when_no_is_held():
    assert lmsr.price_yes(0, 83.2, 100) < 0.5


@pytest.mark.parametrize("q_yes,q_no", [(0, 0), (500, 0), (0, 500), (250, 250), (1000, 5)])
def test_price_stays_a_probability(q_yes, q_no):
    assert 0.0 < lmsr.price_yes(q_yes, q_no, 100) < 1.0


def test_worked_example_first_bet():
    # §5: 50 coins on YES from an empty b=100 market buys ~83.2 shares.
    assert lmsr.shares_for_budget(0, 0, 100, "yes", 50) == pytest.approx(83.2, abs=0.1)


def test_worked_example_second_bet():
    # §5: 50 coins on NO against q_yes=83.2 buys ~114.4 shares.
    assert lmsr.shares_for_budget(83.2, 0, 100, "no", 50) == pytest.approx(114.4, abs=0.1)


@pytest.mark.parametrize("q_yes,q_no,side,budget", [(0, 0, "yes", 50), (40, 25, "yes", 30), (10, 90, "no", 75), (300, 120, "yes", 5)])
def test_budget_round_trips_through_cost(q_yes, q_no, side, budget):
    # The shares a budget buys must cost exactly that budget back through the cost function.
    shares = lmsr.shares_for_budget(q_yes, q_no, 100, side, budget)
    moved = (q_yes + shares, q_no) if side == "yes" else (q_yes, q_no + shares)
    spent = lmsr.cost(*moved, 100) - lmsr.cost(q_yes, q_no, 100)
    assert spent == pytest.approx(budget, abs=1e-6)


def test_a_bigger_budget_buys_more_shares():
    assert lmsr.shares_for_budget(0, 0, 100, "yes", 100) > lmsr.shares_for_budget(0, 0, 100, "yes", 50)


def test_buying_yes_increases_the_yes_price():
    shares = lmsr.shares_for_budget(0, 0, 100, "yes", 40)
    assert lmsr.price_yes(shares, 0, 100) > lmsr.price_yes(0, 0, 100)


@pytest.mark.parametrize("q_yes,q_no", [(83.2, 114.4), (500, 10), (0, 0), (300, 300)])
def test_pool_always_covers_the_winning_payout(q_yes, q_no):
    # Solvency: C(q) >= max(q_yes, q_no), so the pool can always pay the winning side.
    assert lmsr.cost(q_yes, q_no, 100) >= max(q_yes, q_no)


def test_large_quantities_do_not_overflow():
    # The log-sum-exp form keeps huge exponents finite where a naive exp() would be inf.
    assert math.isfinite(lmsr.cost(100000, 0, 100))
    assert lmsr.price_yes(100000, 0, 100) == pytest.approx(1.0)
