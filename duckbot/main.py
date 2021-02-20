import os
import dotenv
import discord
from cogs.duck import Duck
from cogs.tito import Tito
from cogs.typos import Typos
from cogs.bitcoin import Bitcoin
from cogs.insights import Insights
from cogs.kubernetes import Kubernetes
from cogs.announce_day import AnnounceDay
from cogs.thanking_robot import ThankingRobot
from discord.ext import commands


# Load the token from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# Initialize the Discord client
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        for channel in guild.channels:
            print(f"  - channel: {channel.id} (#{channel.name})")
        for emoji in guild.emojis:
            print(f"  - emoji: {emoji}")
        guild_count = guild_count + 1

    print(f"DuckBot is in {guild_count} guilds.")

if __name__ == "__main__":
    bot.add_cog(Duck(bot))
    bot.add_cog(Tito(bot))
    bot.add_cog(Typos(bot))
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(AnnounceDay(bot))
    bot.add_cog(ThankingRobot(bot))
    bot.add_cog(Insights(bot))

    bot.run(os.environ["TOKEN"])
