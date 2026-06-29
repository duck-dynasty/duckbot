from .market import PlayMarket


async def setup(bot):
    from duckbot.db import Database

    await bot.add_cog(PlayMarket(bot, Database()))
