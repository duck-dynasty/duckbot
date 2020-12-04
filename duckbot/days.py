
import datetime
import random

def announce_day_of_week():
    days = {
        "Monday": [
            "the day of the moon",
            "Moonday",
            "Monday",
        ],
        "Tuesday": [
            "Tiw's day",
            "Tuesday",
        ],
        "Wednesday": [
            "Odin's day",
            "Wednesday",
        ],
        "Thursday": [
            "Thor's day",
            "civ",
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
    now = datetime.datetime.now()
    if str(now.hour) == "7":
        day = datetime.datetime.today().strftime('%A')
        return random.choice(templates).format(random.choice(days[day]))

    return None

