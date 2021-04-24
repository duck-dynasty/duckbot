import os
from discord import Intents
from discord.ext import commands
import duckbot.cogs.tito
import duckbot.cogs.robot
import duckbot.cogs.audio
import duckbot.cogs.recipe
import duckbot.cogs.fortune
import duckbot.cogs.weather
import duckbot.cogs.messages
import duckbot.cogs.insights
import duckbot.cogs.formula_one
import duckbot.cogs.corrections
import duckbot.cogs.announce_day
from duckbot.cogs import Duck
from duckbot.server import Channels, Emojis
from duckbot.db import Database
import duckbot.health
import duckbot.util.connection_test


def run_duckbot(bot: commands.Bot):
    if "connection-test" in os.getenv("DUCKBOT_ARGS", ""):
        bot.load_extension(duckbot.util.connection_test.__name__)

    bot.load_extension(duckbot.health.__name__)

    bot.add_cog(Database(bot))

    # server cogs must be loaded first; any references to
    # them should happen in or after the `on_ready` event
    bot.add_cog(Channels(bot))
    bot.add_cog(Emojis(bot))

    bot.add_cog(Duck(bot))
    bot.load_extension(duckbot.cogs.tito.__name__)
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


if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!", help_command=None, intents=intents())
    run_duckbot(bot)
