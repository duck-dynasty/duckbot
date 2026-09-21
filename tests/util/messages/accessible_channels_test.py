from unittest import mock

import discord
import pytest
from discord import Forbidden

from duckbot.util.messages import accessible_channels
from tests.async_mock_ext import list_as_async_generator


@pytest.fixture
def make_text_channel(autospec):
    """Returns a factory for text channels holding the given threads."""

    def make(threads=[], archived=[], readable=True) -> discord.TextChannel:
        channel = autospec.of(discord.TextChannel)
        channel.permissions_for.return_value.read_message_history = readable
        channel.threads = threads
        channel.archived_threads.return_value = list_as_async_generator(archived)
        return channel

    return make


async def collect(guild):
    return [channel async for channel in accessible_channels(guild)]


async def test_yields_channels_and_their_active_and_archived_threads(guild, thread, autospec, make_text_channel):
    archived = autospec.of(discord.Thread)
    channel = make_text_channel(threads=[thread], archived=[archived])
    guild.text_channels = [channel]
    assert await collect(guild) == [channel, thread, archived]


async def test_skips_channels_the_bot_cannot_read(guild, thread, make_text_channel):
    guild.text_channels = [make_text_channel(threads=[thread], readable=False)]
    assert await collect(guild) == []


async def test_skips_forbidden_archived_threads(guild, make_text_channel):
    channel = make_text_channel()
    channel.archived_threads.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [channel]
    assert await collect(guild) == [channel]
