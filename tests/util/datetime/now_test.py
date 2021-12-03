import datetime
from unittest import mock

import duckbot.util.datetime
from duckbot.util.datetime import now


@mock.patch("datetime.datetime")
def test_now_returns_now_in_timezone(dt):
    dt.now.return_value = datetime.datetime(2002, 1, 21, hour=7)
    time = now()
    assert time == datetime.datetime(2002, 1, 21, hour=7)
    dt.now.assert_called_once_with(duckbot.util.datetime.timezone())
