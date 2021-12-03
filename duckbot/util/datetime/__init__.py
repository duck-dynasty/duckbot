import datetime

import pytz


def timezone():
    """
    Returns the default timezone of duckbot.
    :return: US/Eastern
    """
    return pytz.timezone("US/Eastern")


def now():
    """
    Returns the current time in duckbot's default timezone.
    :return: the current time
    """
    return datetime.datetime.now(timezone())
