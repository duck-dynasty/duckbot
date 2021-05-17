import datetime

from duckbot.cogs.announce_day.special_days import SpecialDays


def test_populate_bro_tito_day(bot, guild, emoji):
    bot.emojis = [emoji]
    emoji.guild = guild
    emoji.name = "tito"
    guild.name = "Friends Chat"
    clazz = SpecialDays(bot)
    assert clazz.get_list(datetime.datetime(2020, 5, 7)) == [f"Bro Tito Day {emoji}"]
