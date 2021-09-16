from unittest import mock

import discord
import pytest


@pytest.fixture
@mock.patch("discord.Message", autospec=True)
def message(m, channel, user, member) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    m.channel = channel
    m.author = user if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else member
    return m
