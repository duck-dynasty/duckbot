from datetime import datetime

import pytest

from duckbot.cogs.announce_day.special_days import SpecialDays
from duckbot.util.datetime import timezone


def test_populate_bro_tito_day(bot, guild, emoji):
    bot.emojis = [emoji]
    emoji.guild = guild
    emoji.name = "tito"
    guild.name = "Friends Chat"
    clazz = SpecialDays(bot)
    assert clazz.get_list(datetime(2020, 5, 7)) == [f"Bro Tito Day {emoji}"]


@pytest.mark.parametrize("date", [datetime(2021, 5, 9), datetime(2022, 5, 8), datetime(2023, 5, 14)])
def test_populate_mothers_day(bot, date):
    clazz = SpecialDays(bot)
    assert clazz.get_list(date) == ["Mother's Day"]


@pytest.mark.parametrize("date", [datetime(2021, 6, 20), datetime(2022, 6, 19), datetime(2023, 6, 18)])
def test_populate_fathers_day(bot, date):
    clazz = SpecialDays(bot)
    assert clazz.get_list(date) == ["Father's Day"]


@pytest.mark.parametrize("date", [datetime(2020, 11, 27), datetime(2021, 11, 26), datetime(2022, 11, 25)])
def test_populate_black_friday(bot, date):
    clazz = SpecialDays(bot)
    assert clazz.get_list(date) == ["Black Friday. I hope I can get some new socks"]


@pytest.mark.parametrize("year, seconds", [(2020, -13140.0), (2021, 31522860.0), (2022, 63058860.0)])
def test_populate_duckbot_day(bot, year, seconds):
    clazz = SpecialDays(bot)
    assert clazz.get_list(datetime(year, 12, 3, tzinfo=timezone())) == [f"DuckBot's Inception Day. I'm about {seconds}s old"]


def test_populate_duckbot_day_uses_year_not_populate_time(bot):
    clazz = SpecialDays(bot)
    clazz.get_list(datetime(2022, 6, 1, tzinfo=timezone()))  # triggers _populate(2022) at a non-Dec-3 lookup
    assert clazz.get_list(datetime(2022, 12, 3, tzinfo=timezone())) == ["DuckBot's Inception Day. I'm about 63058860.0s old"]


@pytest.mark.parametrize("date", [datetime(2024, 2, 19), datetime(2025, 2, 17), datetime(2026, 2, 16)])
def test_populate_family_day(bot, date):
    clazz = SpecialDays(bot)
    assert clazz.get_list(date) == ["Family Day"]
