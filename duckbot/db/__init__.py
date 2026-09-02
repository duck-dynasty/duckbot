from .database import Database
from .pg import Pg


# not loaded by default; add duckbot.db to run_duckbot's extensions to enable !pg for a postgres migration
async def setup(bot):
    await bot.add_cog(Pg(bot, Database()))
