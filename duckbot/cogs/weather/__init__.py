from .weather import Weather


def setup(bot):
    from duckbot.db import Database

    bot.add_cog(Weather(bot, Database()))
