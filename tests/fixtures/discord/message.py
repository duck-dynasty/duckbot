import discord
import pytest


@pytest.fixture
def message(raw_message, channel, user, member) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    raw_message.channel = channel
    raw_message.author = user if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else member
    return raw_message


@pytest.fixture
def raw_message(autospec) -> discord.Message:
    """Returns a mock discord message with no properties set."""
    return autospec.of("discord.Message")
