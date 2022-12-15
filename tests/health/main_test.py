from unittest import mock

import pytest

from duckbot.health.__main__ import check


@mock.patch("socket.socket")
def test_check_healthy(socket):
    socket.return_value.__enter__.return_value.recv.return_value = b"healthy"
    with pytest.raises(SystemExit) as e:
        check()
    assert e.value.code == 0
    socket.return_value.__exit__.assert_called()


@mock.patch("socket.socket")
def test_check_unhealthy(socket):
    socket.return_value.__enter__.return_value.recv.return_value = b"unhealthy"
    with pytest.raises(SystemExit) as e:
        check()
    assert e.value.code != 0
    socket.return_value.__exit__.assert_called()


@mock.patch("socket.socket")
def test_check_connection_error(socket):
    socket.return_value.__enter__.return_value.connect.side_effect = Exception("error")
    with pytest.raises(SystemExit) as e:
        check()
    assert e.value.code != 0
    socket.return_value.__exit__.assert_called()
