import random
import datetime
import validators


def get_day_of_week():
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

    now = datetime.datetime.now()
    if str(now.hour) == "7":
        day = datetime.datetime.today().strftime('%A')
        message = random.choice(days[day])

        if validators.url(message):
            return f"A video to start your {day}: {message}"

        return random.choice(templates).format(message)

    return None
# end def get_day_of_week


def get_correction(author, message):
    kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
    for k in kubes:
        if k in message:
            return "I think {0} means K8s".format(author)

    if "k8" in message:
            return "I think {0} means Kubernetes".format(author)

    if "bitcoin" in message:
        return "Magic Beans*"

    return None
# end def get_correction
