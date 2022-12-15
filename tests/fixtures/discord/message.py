import discord
import pytest


@pytest.fixture
def message(request, raw_message, channel, is_private_channel) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    raw_message.channel = channel
    raw_message.guild = None if is_private_channel else request.getfixturevalue("guild")
    raw_message.author = request.getfixturevalue("user" if is_private_channel else "member")
    return raw_message


@pytest.fixture
def raw_message(autospec) -> discord.Message:
    """Returns a mock discord message with no properties set."""
    return autospec.of(discord.Message)
