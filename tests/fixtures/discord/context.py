from unittest import mock

import discord.ext.commands
import pytest


@pytest.fixture
@mock.patch("discord.ext.commands.Context", autospec=True)
def context(c, message) -> discord.ext.commands.Context:
    """Returns a context with nested properties set, for each channel type a command can be sent to."""
    c.message = message
    c.channel = message.channel
    c.author = message.author
    return c
