import datetime
import holidays
import math
from dateutil.relativedelta import relativedelta as rd, SU


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
