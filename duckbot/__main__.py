import os

from discord.ext import commands

import duckbot.cogs.announce_day
import duckbot.cogs.audio
import duckbot.cogs.corrections
import duckbot.cogs.dogs
import duckbot.cogs.duck
import duckbot.cogs.formula_one
import duckbot.cogs.fortune
import duckbot.cogs.games
import duckbot.cogs.github
import duckbot.cogs.google
import duckbot.cogs.insights
import duckbot.cogs.math
import duckbot.cogs.messages
import duckbot.cogs.recipe
import duckbot.cogs.robot
import duckbot.cogs.text
import duckbot.cogs.tito
import duckbot.cogs.weather
import duckbot.health
import duckbot.logs
import duckbot.util.connection_test
from duckbot import DuckBot


def run_duckbot(bot: commands.Bot):
    if "connection-test" in os.getenv("DUCKBOT_ARGS", ""):
        bot.load_extension(duckbot.util.connection_test.__name__)

    bot.load_extension(duckbot.health.__name__)
    bot.load_extension(duckbot.logs.__name__)

    bot.load_extension(duckbot.cogs.duck.__name__)
    bot.load_extension(duckbot.cogs.dogs.__name__)
    bot.load_extension(duckbot.cogs.tito.__name__)
    bot.load_extension(duckbot.cogs.text.__name__)
    bot.load_extension(duckbot.cogs.math.__name__)
    bot.load_extension(duckbot.cogs.games.__name__)
    bot.load_extension(duckbot.cogs.github.__name__)
    bot.load_extension(duckbot.cogs.google.__name__)
    bot.load_extension(duckbot.cogs.recipe.__name__)
    bot.load_extension(duckbot.cogs.fortune.__name__)
    bot.load_extension(duckbot.cogs.weather.__name__)
    bot.load_extension(duckbot.cogs.insights.__name__)
    bot.load_extension(duckbot.cogs.corrections.__name__)
    bot.load_extension(duckbot.cogs.formula_one.__name__)
    bot.load_extension(duckbot.cogs.announce_day.__name__)
    bot.load_extension(duckbot.cogs.robot.__name__)
    bot.load_extension(duckbot.cogs.audio.__name__)
    bot.load_extension(duckbot.cogs.messages.__name__)

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    duckbot.logs.define_logs()
    bot = DuckBot()
    run_duckbot(bot)
