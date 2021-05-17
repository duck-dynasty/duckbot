from unittest import mock

import pytest


@pytest.fixture
@mock.patch("duckbot.slash.Interaction", autospec=True)
def interaction(i):
    return i


@pytest.fixture
@mock.patch("discord.ext.commands.Command", autospec=True)
def command(c):
    return c
