from datetime import datetime
from unittest import mock

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


@mock.patch("duckbot.cogs.announce_day.special_days.now")
@pytest.mark.parametrize(
    "time, seconds",
    [(datetime(2020, 12, 3, 10, 39, tzinfo=timezone()), 0.0), (datetime(2021, 12, 3, 10, 39, tzinfo=timezone()), 31536000.0), (datetime(2022, 12, 3, 10, 39, tzinfo=timezone()), 63072000.0)],
)
def test_populate_duckbot_day(now, bot, time, seconds):
    now.return_value = time
    clazz = SpecialDays(bot)
    assert clazz.get_list(time) == [f"DuckBot's Inception Day. I'm about {seconds}s old"]


@mock.patch("duckbot.cogs.announce_day.special_days.now")
def test_populate_duckbot_day_recomputes_age_on_each_lookup(now, bot):
    inception_day = datetime(2022, 12, 3, 10, 39, tzinfo=timezone())
    earlier = datetime(2022, 6, 1, 12, 0, tzinfo=timezone())
    clazz = SpecialDays(bot)

    now.return_value = earlier
    clazz.get_list(earlier)  # triggers _populate(2022) while now() == earlier

    now.return_value = inception_day
    assert clazz.get_list(inception_day) == [f"DuckBot's Inception Day. I'm about {(inception_day - datetime(2020, 12, 3, 10, 39, tzinfo=timezone())).total_seconds()}s old"]


@pytest.mark.parametrize("date", [datetime(2024, 2, 19), datetime(2025, 2, 17), datetime(2026, 2, 16)])
def test_populate_family_day(bot, date):
    clazz = SpecialDays(bot)
    assert clazz.get_list(date) == ["Family Day"]
