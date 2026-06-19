import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest import mock

import pytest
from discord.ext import commands

from duckbot.cogs.playmarket import config
from duckbot.cogs.playmarket.market import (
    _coins,
    _down,
    _pct,
    _when,
    _whole,
    is_market_admin,
    parse_when,
)

FIXED_NOW = datetime.datetime(2024, 1, 1, 12, 0)


# --- parse_when ----------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("in 1 hour", datetime.timedelta(hours=1)),
        ("in 6 hours", datetime.timedelta(hours=6)),
        ("in 1 day", datetime.timedelta(days=1)),
        ("in 3 days", datetime.timedelta(days=3)),
        ("in 1 week", datetime.timedelta(weeks=1)),
        ("in 2 weeks", datetime.timedelta(weeks=2)),
    ],
)
@mock.patch("duckbot.cogs.playmarket.market.now", return_value=FIXED_NOW)
def test_parse_when_relative(now, text, expected):
    assert parse_when(text) == FIXED_NOW + expected


@mock.patch("duckbot.cogs.playmarket.market.now", return_value=FIXED_NOW)
def test_parse_when_is_case_insensitive(now):
    assert parse_when("IN 3 DAYS") == FIXED_NOW + datetime.timedelta(days=3)


def test_parse_when_absolute_date_and_time():
    parsed = parse_when("2025-07-01 18:00")
    assert (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute) == (2025, 7, 1, 18, 0)


def test_parse_when_absolute_date_only():
    assert parse_when("2025-07-01").date() == datetime.date(2025, 7, 1)


@pytest.mark.parametrize("text", ["whenever", "", "tomorrow", "in three days", "in 3 fortnights", "2025/07/01"])
def test_parse_when_rejects_unparseable_input(text):
    assert parse_when(text) is None


# --- is_market_admin -----------------------------------------------------


async def test_admin_check_rejects_dms():
    ctx = mock.Mock(guild=None)
    with pytest.raises(commands.NoPrivateMessage):
        await is_market_admin(ctx)


async def test_admin_check_rejects_ordinary_members():
    ctx = mock.Mock()
    ctx.bot.is_owner = mock.AsyncMock(return_value=False)
    ctx.author.guild_permissions.manage_guild = False
    with pytest.raises(commands.MissingPermissions):
        await is_market_admin(ctx)


async def test_admin_check_allows_server_managers():
    ctx = mock.Mock()
    ctx.bot.is_owner = mock.AsyncMock(return_value=False)
    ctx.author.guild_permissions.manage_guild = True
    assert await is_market_admin(ctx) is True


async def test_admin_check_allows_the_bot_owner():
    ctx = mock.Mock()
    ctx.bot.is_owner = mock.AsyncMock(return_value=True)
    ctx.author.guild_permissions.manage_guild = False
    assert await is_market_admin(ctx) is True


# --- payout & bond mechanics ---------------------------------------------


def test_winning_yes_pays_one_coin_per_share(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "yes") == 10


def test_winning_no_pays_one_coin_per_share(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "no") == 4


def test_void_pays_half_of_every_share(cog):
    holding = SimpleNamespace(yes_shares=Decimal(10), no_shares=Decimal(4))
    assert cog._payout(holding, "void") == 7


def test_payout_floors_fractional_shares_toward_the_house(cog):
    holding = SimpleNamespace(yes_shares=Decimal("10.9"), no_shares=Decimal(0))
    assert cog._payout(holding, "yes") == 10


def test_void_payout_floors_to_a_whole_coin(cog):
    holding = SimpleNamespace(yes_shares=Decimal(3), no_shares=Decimal(0))  # 1.5 -> 1
    assert cog._payout(holding, "void") == 1


def test_holding_a_bond_moves_coins_from_balance_to_locked(cog):
    player = SimpleNamespace(balance=1000, locked=0)
    cog._hold_bond(player, config.PROPOSE_BOND)
    assert (player.balance, player.locked) == (1000 - config.PROPOSE_BOND, config.PROPOSE_BOND)


def test_releasing_a_bond_is_the_inverse_of_holding(cog):
    player = SimpleNamespace(balance=500, locked=config.PROPOSE_BOND)
    cog._release_bond(player, config.PROPOSE_BOND)
    assert (player.balance, player.locked) == (500 + config.PROPOSE_BOND, 0)


# --- rounding & formatting ----------------------------------------------


def test_whole_floors_a_coin_amount(cog):
    assert _whole(831.776) == 831


def test_whole_never_rounds_up(cog):
    assert _whole(9.999) == 9


def test_down_truncates_shares_toward_the_house():
    assert _down(1.9999999) == Decimal("1.999999")


def test_down_never_rounds_up():
    assert _down(0.0000009) == Decimal("0.000000")


@pytest.mark.parametrize("value,shown", [(10000, "10,000"), (Decimal("831.6"), "832"), (0, "0")])
def test_coins_are_shown_as_whole_numbers(value, shown):
    assert _coins(value) == shown


@pytest.mark.parametrize("probability,shown", [(0.5, "50%"), (0.697, "70%"), (0.0, "0%"), (1.0, "100%")])
def test_prices_are_shown_as_whole_percents(probability, shown):
    assert _pct(probability) == shown


def test_when_is_a_short_timestamp():
    assert _when(datetime.datetime(2025, 7, 1, 18, 0)) == "2025-07-01 18:00"
