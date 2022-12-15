from .weather import Weather


async def setup(bot):
    from duckbot.db import Database

    await bot.add_cog(Weather(bot, Database()))
