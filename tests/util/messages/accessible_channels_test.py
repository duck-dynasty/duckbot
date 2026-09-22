from unittest import mock

import discord
from discord import Forbidden

from duckbot.util.messages import accessible_channels
from tests.async_mock_ext import list_as_async_generator


async def collect(guild):
    return [channel async for channel in accessible_channels(guild)]


async def test_yields_channels_and_their_active_and_archived_threads(guild, text_channel, thread, autospec):
    archived = autospec.of(discord.Thread)
    text_channel.permissions_for.return_value.read_message_history = True
    text_channel.threads = [thread]
    text_channel.archived_threads.return_value = list_as_async_generator([archived])
    guild.text_channels = [text_channel]
    assert await collect(guild) == [text_channel, thread, archived]


async def test_skips_channels_the_bot_cannot_read(guild, text_channel, thread):
    text_channel.permissions_for.return_value.read_message_history = False
    text_channel.threads = [thread]
    guild.text_channels = [text_channel]
    assert await collect(guild) == []


async def test_skips_forbidden_archived_threads(guild, text_channel):
    text_channel.permissions_for.return_value.read_message_history = True
    text_channel.threads = []
    text_channel.archived_threads.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [text_channel]
    assert await collect(guild) == [text_channel]
