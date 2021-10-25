import discord
import pytest


@pytest.fixture
def message(request, raw_message, channel) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    raw_message.channel = channel
    author = "user" if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else "member"
    raw_message.author = request.getfixturevalue(author)
    return raw_message


@pytest.fixture
def raw_message(autospec) -> discord.Message:
    """Returns a mock discord message with no properties set."""
    return autospec.of(discord.Message)
