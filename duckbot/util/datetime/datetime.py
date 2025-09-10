import datetime
from zoneinfo import ZoneInfo


def timezone():
    """
    Returns the default timezone of this module.
    :return: US/Eastern
    """
    return ZoneInfo("US/Eastern")


def now():
    """
    Returns the current time in the default timezone.
    :return: the current time
    """
    return datetime.datetime.now(timezone())
