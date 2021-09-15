import datetime
from unittest import mock

DATETIME = "datetime.datetime"


def patch_now(now):
    """Returns a patched datetime with `now` set to the given time."""
    dt = mock.Mock(wraps=datetime.datetime)
    dt.now.return_value = now
    return mock.patch(DATETIME, new=dt)
