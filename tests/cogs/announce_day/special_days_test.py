from datetime import datetime

import pytest

from duckbot.cogs.announce_day.special_days import SpecialDays


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
