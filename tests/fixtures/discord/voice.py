import discord
import pytest


@pytest.fixture
def voice_channel(autospec) -> discord.VoiceChannel:
    """Returns a voice channel, an audio only channel in a discord server."""
    vc = autospec.of(discord.VoiceChannel)
    vc.type = discord.ChannelType.voice
    return vc


@pytest.fixture
def voice_client(autospec) -> discord.VoiceClient:
    """Returns a mock voice client."""
    return autospec.of(discord.VoiceClient)
