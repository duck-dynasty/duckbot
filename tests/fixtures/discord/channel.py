import discord
import pytest


@pytest.fixture(params=["discord.TextChannel", "discord.DMChannel", "discord.GroupChannel", "discord.Thread"])
def channel(request, text_channel, dm_channel, group_channel, thread):
    """Returns a text based channel."""
    if request.param == "discord.TextChannel":
        return text_channel
    elif request.param == "discord.DMChannel":
        return dm_channel
    elif request.param == "discord.GroupChannel":
        return group_channel
    elif request.param == "discord.Thread":
        return thread
    raise AssertionError


@pytest.fixture
def skip_if_private_channel(channel, dm_channel, group_channel):
    """Skips the test if `channel` is a private channel (a DM or group channel.
    Meant to be used when the `channel` fixture is also used."""
    if channel is dm_channel or channel is group_channel:
        pytest.skip("test requires a non-private discord channel")


@pytest.fixture
def text_channel(autospec) -> discord.TextChannel:
    """Returns a text channel, a typical channel in a discord server."""
    tc = autospec.of("discord.TextChannel")
    tc.type = discord.ChannelType.text
    return tc


@pytest.fixture
def dm_channel(autospec) -> discord.DMChannel:
    """Returns a dm channel, a direct message between two users."""
    dm = autospec.of("discord.DMChannel")
    dm.type = discord.ChannelType.private
    return dm


@pytest.fixture
def group_channel(autospec) -> discord.GroupChannel:
    """Returns a group channel, a private channel between two or more users, outside of a server."""
    g = autospec.of("discord.GroupChannel")
    g.type = discord.ChannelType.group
    return g


@pytest.fixture
def thread(autospec) -> discord.Thread:
    """Returns a thread channel, an ephemeral channel inside of a discord server."""
    thrd = autospec.of("discord.Thread")
    thrd.type = discord.ChannelType.public_thread
    return thrd
