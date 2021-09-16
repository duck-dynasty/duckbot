from unittest import mock

import discord
import pytest


@pytest.fixture
@mock.patch("discord.VoiceChannel", autospec=True)
def voice_channel(vc) -> discord.VoiceChannel:
    """Returns a voice channel, an audio only channel in a discord server."""
    vc.type = discord.ChannelType.voice
    return vc


@pytest.fixture
@mock.patch("discord.VoiceClient", autospec=True)
def voice_client(vc) -> discord.VoiceClient:
    """Returns a mock voice client."""
    return vc
