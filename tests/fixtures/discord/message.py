import discord
import pytest


@pytest.fixture
def message(autospec, channel, user, member) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    m = autospec.of("discord.Message")
    m.channel = channel
    m.author = user if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else member
    return m
