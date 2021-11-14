import os
import pkgutil

from discord.ext import commands

import duckbot.cogs
import duckbot.health
import duckbot.logs
import duckbot.slash
import duckbot.util.connection_test
from duckbot import DuckBot


def run_duckbot(bot: commands.Bot):
    bot.load_extension(duckbot.logs.__name__)

    if "connection-test" in os.getenv("DUCKBOT_ARGS", ""):
        bot.load_extension(duckbot.util.connection_test.__name__)

    bot.load_extension(duckbot.health.__name__)
    bot.load_extension(duckbot.slash.__name__)

    for extension in (x for x in pkgutil.iter_modules(duckbot.cogs.__path__) if x.ispkg):
        bot.load_extension(f"{duckbot.cogs.__name__}.{extension.name}")

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    run_duckbot(DuckBot())
