import os
import tools
import days
import dotenv
import discord
import datetime
from discord.ext import commands, tasks

# Load the token from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# Initialize the Discord client
bot = discord.Client()


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

    print("DuckBot is in " + str(guild_count) + " channels.")
# end def on_ready


@bot.event
async def on_message(message):
    author = str(message.author).split("#")[0]
    print(author)

    if message.author == bot.user:
        return

    correction = tools.make_correction(author, message.content.lower())
    if correction is not None:
        await message.channel.send(correction)
# end def on_message


@tasks.loop(hours=1)
async def on_hour():
    day = days.announce_day_of_week
    if day is not None:
        channel = bot.get_channel(780860661675720765)
        await channel.send(day)
    
    return
# end def on_hour


if __name__ == "__main__":
    bot.run(os.environ["TOKEN"])
