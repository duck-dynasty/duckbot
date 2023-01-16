import datetime
from unittest import mock

import pytz

from duckbot.util.datetime import now, timezone


def test_timezone_returns_us_eastern():
    tz = timezone()
    assert tz == pytz.timezone("US/Eastern")


@mock.patch("datetime.datetime")
def test_now_returns_now_in_default_timezone(dt):
    dt.now.return_value = datetime.datetime(2002, 1, 21, hour=7)
    time = now()
    assert time == datetime.datetime(2002, 1, 21, hour=7)
    dt.now.assert_called_once_with(pytz.timezone("US/Eastern"))
