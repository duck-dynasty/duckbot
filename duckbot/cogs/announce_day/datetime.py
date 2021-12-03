import datetime

import pytz


def timezone():
    """
    Returns the default timezone of this module.
    :return: US/Eastern
    """
    return pytz.timezone("US/Eastern")


def now():
    """
    Returns the current time in the default timezone.
    :return: the current time
    """
    return datetime.datetime.now(timezone())
