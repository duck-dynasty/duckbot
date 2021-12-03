import pytz

from duckbot.util.datetime import timezone


def test_timezone_returns_us_eastern():
    tz = timezone()
    assert tz == pytz.timezone("US/Eastern")
