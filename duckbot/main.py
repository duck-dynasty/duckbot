import os
import tools
import dotenv
import discord
import datetime
from discord.ext import commands, tasks


days = {
    "Monday": "the day of the moon",
    "Tuesday": "Tiw's day",
    "Wednesday": "Odin's day",
    "Thursday": "Thor's day",
    "Friday": "Frigga's day",
    "Saturday": "Satun's day",
    "Sunday": "the day of the sun",
}


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
async def called_once_a_day2():
    message_channel = bot.get_channel(780860661675720765)
    
    now = datetime.datetime.now()
    if str(now.hour) == "7":
        day = datetime.datetime.today().strftime('%A')
        await message_channel.send("Yoooooo, today is {0}! Brother.".format(days[day]))
    
    return
# end def called_once_a_day2


if __name__ == "__main__":
    bot.run(os.environ["TOKEN"])
