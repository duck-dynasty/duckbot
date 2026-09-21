from unittest import mock

import discord
from discord import Forbidden

from duckbot.util.messages import accessible_channels
from tests.async_mock_ext import list_as_async_generator


def channel(autospec, spec, threads=[], archived=[], readable=True):
    mocked = autospec.of(spec)
    mocked.permissions_for.return_value.read_message_history = readable
    if hasattr(mocked, "archived_threads"):
        mocked.threads = threads
        mocked.archived_threads.return_value = list_as_async_generator(archived)
    return mocked


async def collect(guild):
    return [channel async for channel in accessible_channels(guild)]


async def test_yields_messageable_channels(guild, autospec):
    text = channel(autospec, discord.TextChannel)
    voice = channel(autospec, discord.VoiceChannel)
    stage = channel(autospec, discord.StageChannel)
    guild.channels = [text, voice, stage]
    assert await collect(guild) == [text, voice, stage]


async def test_skips_categories_and_forum_channels_themselves(guild, autospec):
    guild.channels = [channel(autospec, discord.CategoryChannel), channel(autospec, discord.ForumChannel)]
    assert await collect(guild) == []


async def test_yields_active_and_archived_threads(guild, thread, autospec):
    archived = autospec.of(discord.Thread)
    forum = channel(autospec, discord.ForumChannel, threads=[thread], archived=[archived])
    guild.channels = [forum]
    assert await collect(guild) == [thread, archived]


async def test_skips_forbidden_archived_threads(guild, autospec):
    text = channel(autospec, discord.TextChannel)
    text.archived_threads.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.channels = [text]
    assert await collect(guild) == [text]


async def test_skips_channels_the_bot_cannot_read(guild, thread, autospec):
    guild.channels = [channel(autospec, discord.TextChannel, threads=[thread], readable=False)]
    assert await collect(guild) == []
