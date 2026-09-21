from unittest import mock

import discord
from discord import Forbidden

from duckbot.util.messages import accessible_channels
from tests.async_mock_ext import list_as_async_generator


def text_channel_with(autospec, threads=[], archived=[], readable=True):
    channel = autospec.of(discord.TextChannel)
    channel.permissions_for.return_value.read_message_history = readable
    channel.threads = threads
    channel.archived_threads.return_value = list_as_async_generator(archived)
    return channel


async def collect(guild):
    return [channel async for channel in accessible_channels(guild)]


async def test_yields_channels_and_their_active_and_archived_threads(guild, thread, autospec):
    archived = autospec.of(discord.Thread)
    channel = text_channel_with(autospec, threads=[thread], archived=[archived])
    guild.text_channels = [channel]
    assert await collect(guild) == [channel, thread, archived]


async def test_skips_channels_the_bot_cannot_read(guild, thread, autospec):
    guild.text_channels = [text_channel_with(autospec, threads=[thread], readable=False)]
    assert await collect(guild) == []


async def test_skips_forbidden_archived_threads(guild, autospec):
    channel = text_channel_with(autospec)
    channel.archived_threads.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [channel]
    assert await collect(guild) == [channel]
