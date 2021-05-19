from unittest import mock

import pytest
from discord.http import HTTPClient


@pytest.fixture(autouse=True)
def add_bot_connection(bot):
    bot._connection = mock.Mock()
    bot.http = mock.MagicMock(spec=HTTPClient)


@pytest.fixture
@mock.patch("duckbot.slash.Interaction", autospec=True)
def interaction(i):
    return i


@pytest.fixture
@mock.patch("discord.ext.commands.Command", autospec=True)
def command(c):
    return c
