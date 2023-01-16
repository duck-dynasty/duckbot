import math
from datetime import date, datetime

import discord
import holidays
from dateutil.relativedelta import FR, SU
from dateutil.relativedelta import relativedelta as rd

from duckbot.util.datetime import now, timezone


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

        tito = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="tito")

        self[date(year, 1, 1)] = f"Male Kelly's birthday. He's {year-1900} years old according to most websites"
        self[date(year, 1, 31)] = f"Erin and Taras' Anniversary. It's been {year-2010} entire years"
        self[date(year, 2, 2)] = "Groundhog Day"
        self[date(year, 2, 14)] = "Valentine's Day"
        self[date(year, 3, 9)] = f"Lachlan's Birthday. He is {year-1989} years old. All hail this magnificent and unsurpassed achievement in longevity. Glory be unto him"
        self[date(year, 3, 14)] = f"Pi Day ({math.pi})"
        self[date(year, 3, 17)] = "St. Patrick's Day"
        self[date(year, 3, 20)] = f"Tom and Kelly's real wedding anniversary. They've been real together for {year-2015} years"
        self[date(year, 3, 25)] = "The Day the One Ring was cast into the fires of Mt. Doom, bringing about the fall of Sauron"
        self[date(year, 4, 12)] = "National Grilled Cheese Day"
        self[date(year, 5, 1) + rd(weekday=SU(+2))] = "Mother's Day"
        self[date(year, 5, 7)] = f"Bro Tito Day {tito}"
        self[date(year, 5, 25)] = "Towel Day! DON'T PANIC :thumbsup:"
        self[date(year, 6, 1) + rd(weekday=SU(+3))] = "Father's Day"
        self[date(year, 6, 21)] = f"Erin's Birthday. She's {year-1991} years old"
        self[date(year, 9, 8)] = f"Dan's Birthday. He {year-1989} old. :headstone: to a legend"
        self[date(year, 9, 26)] = f"Tom's Birthday. He's {year-1990} years old. How he made it this far, we'll never know"
        self[date(year, 10, 7)] = f"Delta's Birthday. He's {year-2015} years old and is a good boy"
        self[date(year, 10, 9)] = "Leif Erikson Day. Hinga Dinga Durgen! https://tenor.com/view/viking-spongebob-squarepants-durgen-fall-down-hard-gif-7302846 "  # intentional trailing space for gif
        self[date(year, 10, 31)] = "Halloween"
        self[date(year, 11, 10)] = f"Tom and Kelly's fake wedding anniversary. They've been fake together for {year-2014} years"
        self[date(year, 11, 12)] = f"Sabrina's Birthday. She is {year-1996} years old. Good work on surviving"
        self[date(year, 11, 14)] = f"Male Kelly's birthday... Maybe... idk. He's around {year - 1989} years old now."
        self[date(year, 11, 1) + rd(weekday=FR(+4))] = "Black Friday. I hope I can get some new socks"
        self[date(year, 12, 2)] = f"Female Kelly's Birthday. She's {year-1989} years old"
        self[date(year, 12, 3)] = f"DuckBot's Inception Day. I'm about {(now()-datetime(2020, 12, 3, 10, 39, tzinfo=timezone())).total_seconds()}s old"
        self[date(year, 12, 5)] = f"Taras' Birthday. He's {year-1989} years old"
