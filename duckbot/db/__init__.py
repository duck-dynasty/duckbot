from .database import Database
from .pg import Pg


async def setup(bot):
    await bot.add_cog(Pg(bot, Database()))
