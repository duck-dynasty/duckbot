import os
import dotenv
import discord
import datetime
import bitcoin
import kubernetes
from discord.ext import commands, tasks


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

        guild_count = guild_count + 1

    print("DuckBot is in " + str(guild_count) + " channels.")


"""
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)  # so commands will still get called
# end def on_message


@tasks.loop(hours=1)
async def on_hour():
    day = tools.get_day_of_week()
    if day is not None:
        channel = bot.get_channel(780860661675720765)
        await channel.send(day)
    
    return
# end def on_hour
"""


if __name__ == "__main__":
    bot.add_cog(bitcoin.Bitcoin(bot))
    bot.add_cog(kubernetes.Kubernetes(bot))
    bot.run(os.environ["TOKEN"])
