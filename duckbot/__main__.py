import os
from discord import Intents
from discord.ext import commands
import duckbot.cogs.audio
import duckbot.cogs.announce_day
from duckbot.cogs import Duck, Tito, Typos, Recipe, Bitcoin, Insights, Kubernetes, ThankingRobot, Weather, FormulaOne, Fortune, MessageModified
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
    bot.add_cog(Tito(bot))
    bot.add_cog(Typos(bot))
    bot.add_cog(Recipe(bot))
    bot.add_cog(Fortune(bot))
    bot.add_cog(Weather(bot))
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Insights(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(FormulaOne(bot))
    bot.load_extension(duckbot.cogs.announce_day.__name__)
    bot.add_cog(ThankingRobot(bot))
    bot.load_extension(duckbot.cogs.audio.__name__)
    bot.add_cog(MessageModified(bot))

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
