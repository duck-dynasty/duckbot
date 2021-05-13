import logging
import logging.handlers
import os
from discord import Intents, Game
from discord.ext import commands
import duckbot.cogs.duck
import duckbot.cogs.dogs
import duckbot.cogs.tito
import duckbot.cogs.games
import duckbot.cogs.robot
import duckbot.cogs.audio
import duckbot.cogs.fortune
import duckbot.cogs.recipe
import duckbot.cogs.weather
import duckbot.cogs.messages
import duckbot.cogs.insights
import duckbot.cogs.corrections
import duckbot.cogs.formula_one
import duckbot.cogs.announce_day
import duckbot.health
import duckbot.util.connection_test


def run_duckbot(bot: commands.Bot):
    if "connection-test" in os.getenv("DUCKBOT_ARGS", ""):
        bot.load_extension(duckbot.util.connection_test.__name__)

    bot.load_extension(duckbot.health.__name__)

    bot.load_extension(duckbot.cogs.duck.__name__)
    bot.load_extension(duckbot.cogs.dogs.__name__)
    bot.load_extension(duckbot.cogs.tito.__name__)
    bot.load_extension(duckbot.cogs.games.__name__)
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


def intents() -> Intents:
    intent = Intents.default()
    intent.members = False
    intent.presences = False
    intent.bans = False
    intent.integrations = False
    intent.webhooks = False
    intent.invites = False
    intent.webhooks = False
    intent.typing = False
    return intent


def logger_setup():
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(filename=os.path.join(log_directory, "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)


if __name__ == "__main__":
    logger_setup()
    bot = commands.Bot(command_prefix="!", help_command=None, intents=intents(), activity=Game(name="Duck Game"))
    run_duckbot(bot)
