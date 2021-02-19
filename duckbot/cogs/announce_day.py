import random
import cogs.channels as channels
import datetime
import pytz
import validators
from discord.ext import commands, tasks


days = {
    0: {
        "names": [
            "the day of the moon",
            "Moonday",
            "Monday",
        ],
        "templates": [
            "Screw this, it is {0}.",
        ],
    },
    1: {
        "names": [
            "Tyr's day",
            "Tuesday",
            "Dndndndndndndnd"
        ],
        "templates": [
            "Yo, one of my favourite days ever: {0}.",
        ],
    },
    2: {
        "names": [
            "Odin's day",
            "Wednesday",
            "Wednesday, my dudes",
            "hump day",
            "Ness' wedding day",
            "https://www.youtube.com/watch?v=du-TY1GUFGk",
        ],
        "templates": [
        ],
    },
    3: {
        "names": [
            "Thor's day",
            "Thorsday",
            "civ day",
            "Thursday",
        ],
        "templates": [
        ],
    },
    4: {
        "names": [
            "Frigga's day",
            "Friday, Friday, gotta get down on Friday",
            "Friday",
        ],
        "templates": [
        ],
    },
    5: {
        "names": [
            "Saturn's day",
            "Saturday",
        ],
        "templates": [
            "WEEKEND ALERT: {0}!",
        ],
    },
    6: {
        "names": [
            "the day of the sun",
            "Sunday",
            "Sunday, Sunday, Sunday",
        ],
        "templates": [
            "WEEKEND ALERT: {0}!",
        ],
    },
}

templates = [
    "Today is {0}.",
    "Today: {0}. Tomorrow: {1}.",
    "Brothers, the day is {0}.",
    "Yoooooo, today is {0}! Brother.",
    "The day is {0}. Prepare yourself.",
    "What if I said to you that in fact, today is not {0}? I'd be lying.",
    "What if I said to you that infact, today is not {1}? I'd be right. It's {0}.",
    "Rejoice, for today is {0}.",
    "Don't get it twisted, it's {0}.",
    "{0}",
    "It {0}.",
    "Today is {0}, I hope you have your pants on.",
    "Gentlemen, it is with great pleasure that I inform you. Today is {0}.",
    "Huh, it's {0}, but it feels more like {1}.",
    "The day of the week according to the Gregorian calendar is {0}.",
    "Beep boop: {0}.",
    "I take no pleasure in announcing that today is {0}, for I am a robot.",
    "I take no displeasure in announcing that today is {0}, for I am a robot.",
]


class AnnounceDay(commands.Cog):

    def __init__(self, bot, start_tasks=True):
        self.bot = bot
        self.tz = pytz.timezone("US/Eastern")
        if start_tasks:
            self.on_hour.start()

    def cog_unload(self):
        self.on_hour.cancel()

    def should_announce_day(self):
        now = datetime.datetime.now(self.tz)
        return now.hour == 7

    def get_message(self):
        day = datetime.datetime.now(self.tz).weekday()
        today = random.choice(days[day]["names"])
        tomorrow = random.choice(days[(day + 1) % 7]["names"])
        return random.choice(templates + days[day]["templates"]).format(today, tomorrow)

    @tasks.loop(hours=1.0)
    async def on_hour(self):
        await self.__on_hour()
    async def __on_hour(self):
        if self.should_announce_day():
            channel = self.bot.get_channel(channels.GENERAL)
            message = self.get_message()
            await channel.send(message)

    @on_hour.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name = "day")
    async def day_command(self, context):
        await context.send(self.get_message())
