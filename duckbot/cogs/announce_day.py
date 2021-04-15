import random
import datetime
import pytz
import holidays
import math
from dateutil.relativedelta import relativedelta as rd, SU
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
            "Dndndndndndndnd",
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
        "templates": [],
    },
    3: {
        "names": [
            "Thor's day",
            "Thorsday",
            "civ day",
            "Thursday",
        ],
        "templates": [],
    },
    4: {
        "names": [
            "Frigga's day",
            "Friday, Friday, gotta get down on Friday",
            "Friday",
        ],
        "templates": [],
    },
    5: {
        "names": [
            "Tom's Movie Night",
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
    "What if I said to you that in fact, today is not {1}? I'd be right. It's {0}.",
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
        self.holidays = SpecialDays(bot)
        if start_tasks:
            self.on_hour.start()

    def cog_unload(self):
        self.on_hour.cancel()

    def should_announce_day(self):
        now = datetime.datetime.now(self.tz)
        return now.hour == 7

    def get_message(self):
        now = datetime.datetime.now(self.tz)
        day = now.weekday()
        today = random.choice(days[day]["names"])
        tomorrow = random.choice(days[(day + 1) % 7]["names"])
        message = random.choice(templates + days[day]["templates"]).format(today, tomorrow)
        if now in self.holidays:
            specials = " and ".join(self.holidays.get_list(now))
            return message + "\n" + "It is also " + specials + "."
        else:
            return message

    @tasks.loop(hours=1.0)
    async def on_hour(self):
        await self.__on_hour()

    async def __on_hour(self):
        if self.should_announce_day():
            channel = self.bot.get_cog("channels").get_general_channel()
            message = self.get_message()
            await channel.send(message)

    @on_hour.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="day")
    async def day_command(self, context):
        await context.send(self.get_message())


class SpecialDays(holidays.Canada):
    """A list of holidays and other special days according to the bot.
    `holidays.Canada` only supports stat days, so also add in non-stat days.
    @see https://github.com/dr-prodigy/python-holidays/blob/master/holidays/countries/canada.py
    """

    def __init__(self, bot):
        holidays.Canada.__init__(self)
        self.bot = bot

    def _populate(self, year):
        holidays.Canada._populate(self, year)

        self[datetime.date(year, 1, 31)] = f"Erin and Taras' Anniversary. It's been {year-2010} entire years"
        self[datetime.date(year, 2, 2)] = "Groundhog Day"
        self[datetime.date(year, 2, 14)] = "Valentine's Day"
        self[datetime.date(year, 3, 9)] = f"Lachlan's Birthday. He is {year-1989} years old. All hail this magnificent and unsurpassed achievement in longevity. Glory be unto him"
        self[datetime.date(year, 3, 14)] = f"Pi Day ({math.pi})"
        self[datetime.date(year, 3, 17)] = "St. Patrick's Day"
        self[datetime.date(year, 3, 20)] = f"Tom and Kelly's real wedding anniversary. They've been real together for {year-2015} years"
        self[datetime.date(year, 3, 25)] = "The Day the One Ring was cast into the fires of Mt. Doom, bringing about the fall of Sauron"
        self[datetime.date(year, 4, 12)] = "National Grilled Cheese Day"
        self[datetime.date(year, 5, 1) + rd(weekday=SU(+2))] = "Mother's Day"
        self[datetime.date(year, 5, 7)] = f"Bro Tito Day {self.bot.get_cog('emojis').get_emoji_by_name('tito')}"
        self[datetime.date(year, 6, 1) + rd(weekday=SU(+3))] = "Father's Day"
        self[datetime.date(year, 6, 21)] = f"Erin's Birthday. She's {year-1991} years old"
        self[datetime.date(year, 9, 8)] = f"Dan's Birthday. He {year-1989} old"
        self[datetime.date(year, 9, 26)] = f"Tom's Birthday. He's {year-1990} years old. How he made it this far, we'll never know"
        self[datetime.date(year, 10, 5)] = f"Delta's Birthday. He's {year-2015} years old and is a good boy"
        self[datetime.date(year, 10, 31)] = "Halloween"
        self[datetime.date(year, 11, 10)] = f"Tom and Kelly's fake wedding anniversary. They've been fake together for {year-2014} years"
        self[datetime.date(year, 11, 12)] = f"Sabrina's Birthday. She is {year-1996} years old. Good work on surviving"
        self[datetime.date(year, 12, 2)] = f"Female Kelly's Birthday. She's {year-1989} years old"
        self[datetime.date(year, 12, 3)] = "DuckBot's Inception Day"
        self[datetime.date(year, 12, 5)] = f"Taras' Birthday. He's {year-1989} years old"
