import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from duckbot.cogs.playmarket.market import (
    PlayMarket,
    _coins,
    _down,
    _next_quarter_start,
    _pct,
    _whole,
)


@pytest.fixture
def cog(bot, db):
    market = PlayMarket(bot, db)
    market.tick_loop.cancel()
    return market


# --- payout mechanics ----------------------------------------------------


def test_winning_yes_pays_one_coin_per_share(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "yes", -7) == 10


def test_winning_no_pays_one_coin_per_share(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "no", -7) == 4


def test_void_refunds_the_net_stake(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "void", -99) == 99


def test_void_never_claws_back_realised_profit(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(0))
    assert cog._payout(holding, "void", 25) == 0


def test_payout_floors_fractional_shares_toward_the_house(cog):
    holding = SimpleNamespace(yes_shares=Decimal("10.9"), no_shares=Decimal(0))
    assert cog._payout(holding, "yes", -7) == 10


# --- rounding & formatting ----------------------------------------------


def test_whole_floors_a_coin_amount():
    assert _whole(831.776) == 831


def test_whole_never_rounds_up():
    assert _whole(9.999) == 9


def test_down_truncates_shares_toward_the_house():
    assert _down(1.9999999) == Decimal("1.999999")


def test_down_never_rounds_up():
    assert _down(0.0000009) == Decimal("0.000000")


@pytest.mark.parametrize("value,shown", [(10000, "10,000"), (Decimal("831.6"), "832"), (0, "0")])
def test_coins_are_shown_as_whole_numbers(value, shown):
    assert _coins(value) == shown


@pytest.mark.parametrize("probability,shown", [(0.5, "50%"), (0.697, "69.7%"), (0.0, "0%"), (1.0, "100%"), (0.0193, "1.93%")])
def test_prices_keep_a_few_decimal_places(probability, shown):
    assert _pct(probability) == shown


# --- quarter alignment -----------------------------------------------------


@pytest.mark.parametrize(
    "dt,expected",
    [
        (datetime.datetime(2024, 1, 1, 12, 0), datetime.datetime(2024, 4, 1)),
        (datetime.datetime(2024, 3, 31, 23, 59), datetime.datetime(2024, 4, 1)),
        (datetime.datetime(2024, 4, 1, 0, 0), datetime.datetime(2024, 7, 1)),
        (datetime.datetime(2024, 10, 15), datetime.datetime(2025, 1, 1)),
        (datetime.datetime(2024, 12, 31, 23, 59), datetime.datetime(2025, 1, 1)),
    ],
)
def test_next_quarter_start_lands_on_the_following_quarter(dt, expected):
    assert _next_quarter_start(dt) == expected
