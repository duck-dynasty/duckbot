from unittest import mock
import datetime

DATETIME = "datetime.datetime"


def patch_now(now):
    """Returns a patched datetime with `now` set to the given time."""
    dt = mock.Mock(wraps=datetime.datetime)
    dt.now.return_value = now
    return mock.patch(DATETIME, new=dt)


def patch_utcnow(utcnow):
    """Returns a patched datetime with `utcnow` set to the given time."""
    dt = mock.Mock(wraps=datetime.datetime)
    dt.utcnow.return_value = utcnow
    return mock.patch(DATETIME, new=dt)
