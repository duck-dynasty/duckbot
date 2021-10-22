import discord
import pytest


@pytest.fixture
def interaction(autospec, message) -> discord.Interaction:
    """Returns an interaction with nested properties set, for each channel type a command can be sent to."""
    i = autospec.of(discord.Interaction)
    i.message = message
    i.channel = message.channel
    i.guild = message.guild
    i.user = message.author
    return i
