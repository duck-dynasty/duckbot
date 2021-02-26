import os
import sys
import dotenv
from cogs.duck import Duck
from cogs.tito import Tito
from cogs.typos import Typos
from cogs.recipe import Recipe
from cogs.bitcoin import Bitcoin
from cogs.insights import Insights
from cogs.kubernetes import Kubernetes
from cogs.announce_day import AnnounceDay
from cogs.thanking_robot import ThankingRobot
from discord.ext import commands
from server.channels import Channels
from server.emojis import Emojis


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='!', help_command=None)

    # server cogs must be loaded first; any references to
    # them should happen in or after the `on_ready` event
    bot.add_cog(Channels(bot))
    bot.add_cog(Emojis(bot))

    bot.add_cog(Duck(bot))
    bot.add_cog(Tito(bot))
    bot.add_cog(Typos(bot))
    bot.add_cog(Recipe(bot))
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Insights(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(AnnounceDay(bot))
    bot.add_cog(ThankingRobot(bot))

    if "dry-run" not in sys.argv:
        # load the token from .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        dotenv.load_dotenv(dotenv_path)
        bot.run(os.environ["TOKEN"])
