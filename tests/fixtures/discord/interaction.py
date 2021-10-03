import discord
import pytest


@pytest.fixture
def interaction(request, autospec, channel) -> discord.Interaction:
    """Returns an interaction with nested properties set, for each channel type a command can be sent to."""
    i = autospec.of("discord.Interaction")
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    i.channel = channel
    author = "user" if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else "member"
    i.user = request.getfixturevalue(author)
    return i
