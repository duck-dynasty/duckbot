import discord.ext.commands
import pytest


@pytest.fixture
def context(autospec, message) -> discord.ext.commands.Context:
    """Returns a context with nested properties set, for each channel type a command can be sent to."""
    c = autospec.of("discord.ext.commands.Context")
    c.message = message
    c.channel = message.channel
    c.author = message.author
    return c
