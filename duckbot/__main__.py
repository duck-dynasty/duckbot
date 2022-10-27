import asyncio
import os
import pkgutil

from discord.ext import commands

import duckbot.cogs
import duckbot.health
import duckbot.logs
import duckbot.slash
import duckbot.util.connection_test
from duckbot import DuckBot


async def run_duckbot(bot: commands.Bot):
    await bot.load_extension(duckbot.logs.__name__)

    if "connection-test" in os.getenv("DUCKBOT_ARGS", ""):
        await bot.load_extension(duckbot.util.connection_test.__name__)

    await bot.load_extension(duckbot.health.__name__)
    await bot.load_extension(duckbot.slash.__name__)

    for extension in (x for x in pkgutil.iter_modules(duckbot.cogs.__path__) if x.ispkg):
        await bot.load_extension(f"{duckbot.cogs.__name__}.{extension.name}")

    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(run_duckbot(DuckBot()))
