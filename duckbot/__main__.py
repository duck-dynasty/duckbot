import os
import sys
from discord.ext import commands
from duckbot.cogs import Duck, Tito, Typos, Recipe, Bitcoin, Insights, Kubernetes, AnnounceDay, ThankingRobot, Weather
from duckbot.server import Channels, Emojis


if __name__ == "__main__":
    bot = commands.Bot(command_prefix="!", help_command=None)

    # server cogs must be loaded first; any references to
    # them should happen in or after the `on_ready` event
    bot.add_cog(Channels(bot))
    bot.add_cog(Emojis(bot))

    bot.add_cog(Duck(bot))
    bot.add_cog(Tito(bot))
    bot.add_cog(Typos(bot))
    bot.add_cog(Recipe(bot))
    bot.add_cog(Weather(bot))
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Insights(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(AnnounceDay(bot))
    bot.add_cog(ThankingRobot(bot))

    if "dry-run" not in sys.argv:
        bot.run(os.getenv("DISCORD_TOKEN"))
