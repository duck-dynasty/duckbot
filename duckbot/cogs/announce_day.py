import random
import cogs.channels as channels
import datetime
import pytz
import validators
from discord.ext import commands, tasks


days = {
    "Monday": [
        "the day of the moon",
        "Moonday",
        "Monday",
    ],
    "Tuesday": [
        "Tiw's day",
        "Tuesday",
        "Dndndndndndndnd"
    ],
    "Wednesday": [
        "Odin's day",
        "Wednesday",
        "Wednesday, my dudes",
        "https://www.youtube.com/watch?v=du-TY1GUFGk",
    ],
    "Thursday": [
        "Thor's day",
        "civ day",
        "Thursday",
    ],
    "Friday": [
        "Frigga's day",
        "Friday, Friday, gotta get down on Friday",
        "Friday",
    ],
    "Saturday": [
        "Saturn's day",
        "Saturday",
    ],
    "Sunday": [
        "the day of the sun",
        "Sunday",
    ],
}

templates = [
    "Yoooooo, today is {0}! Brother.",
    "The day is {0}. Prepare yourself.",
    "What if I said to you that in fact, today is not {0}? I'd be lying.",
]


class AnnounceDay(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.on_hour.start()

    def cog_unload(self):
        self.on_hour.cancel()

    def get_day_of_week(self):
        day = datetime.datetime.today().strftime('%A')
        message = random.choice(days[day])

        if validators.url(message):
            return f"A video to start your {day}: {message}"

        return random.choice(templates).format(message)

    @tasks.loop(hours=1.0)
    async def on_hour(self):
        now = datetime.datetime.now(pytz.timezone("US/Eastern"))
        if now.hour == 7:
            channel = self.bot.get_channel(channels.GENERAL)
            day = self.get_day_of_week()
            await channel.send(day)

    @on_hour.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
