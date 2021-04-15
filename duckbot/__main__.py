import os
import sys
from discord.ext import commands
from duckbot.cogs import Duck, Tito, Typos, Recipe, Bitcoin, Insights, Kubernetes, AnnounceDay, ThankingRobot, Weather, WhoCanItBeNow, Fortune, MessageModified
from duckbot.server import Channels, Emojis
from duckbot.db import Database
from duckbot.health import HealthCheck
from duckbot.util import ConnectionTest


def duckbot(bot):
    if "connection-test" in sys.argv:
        bot.add_cog(ConnectionTest(bot))

    bot.add_cog(HealthCheck(bot))

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
    bot.add_cog(AnnounceDay(bot))
    bot.add_cog(ThankingRobot(bot))
    bot.add_cog(WhoCanItBeNow(bot))
    bot.add_cog(MessageModified(bot))

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!", help_command=None)
    duckbot(bot)
