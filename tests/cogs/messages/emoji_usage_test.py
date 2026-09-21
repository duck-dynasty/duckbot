import datetime
from unittest import mock

import discord
import pytest
from discord import Embed, Forbidden
from discord.ext import commands

from duckbot.cogs.messages import EmojiUsage
from tests.async_mock_ext import list_as_async_generator
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz() -> EmojiUsage:
    return bind_commands(EmojiUsage())


@pytest.fixture
def make_emoji(autospec):
    def make(id, name, animated=False) -> discord.Emoji:
        emoji = autospec.of(discord.Emoji)
        emoji.id = id
        emoji.name = name
        emoji.__str__ = lambda x: f"<{'a' if animated else ''}:{name}:{id}>"
        return emoji

    return make


@pytest.fixture
def make_message(autospec):
    def make(content="", reactions=[]) -> discord.Message:
        message = autospec.of(discord.Message)
        message.content = content
        message.reactions = reactions
        return message

    return make


@pytest.fixture
def make_reaction(autospec):
    def make(emoji, count=1) -> discord.Reaction:
        reaction = autospec.of(discord.Reaction)
        reaction.emoji = emoji
        reaction.count = count
        return reaction

    return make


def readable(channel, messages):
    channel.history.return_value = list_as_async_generator(messages)
    channel.permissions_for.return_value.read_message_history = True
    if hasattr(channel, "archived_threads"):
        channel.threads = []
        channel.archived_threads.return_value = list_as_async_generator([])
    return channel


async def test_emoji_usage_command_is_rejected_outside_a_guild(clazz, context):
    context.guild = None
    with pytest.raises(commands.NoPrivateMessage):
        any(check(context) for check in clazz.emoji_usage.checks)


async def test_emoji_usage_sends_report(clazz, guild, text_channel, context, make_emoji, make_message):
    duck = make_emoji(1, "duck")
    guild.emojis = [duck]
    guild.text_channels = [readable(text_channel, [make_message(f"{duck} hello")])]
    context.guild = guild
    await clazz.emoji_usage(context)
    context.send.assert_called_once_with(embed=Embed(title="Emoji Usage \N{MIDDLE DOT} last 90 days", description=f"{duck} 1"))


@mock.patch("duckbot.cogs.messages.emoji_usage.now", return_value=datetime.datetime(2026, 9, 21, tzinfo=datetime.timezone.utc))
async def test_gather_counts_looks_back_the_given_days(now, clazz, guild, text_channel):
    guild.emojis = []
    guild.text_channels = [readable(text_channel, [])]
    await clazz.gather_counts(guild, 7)
    text_channel.history.assert_called_once_with(limit=None, after=datetime.datetime(2026, 9, 14, tzinfo=datetime.timezone.utc))


async def test_gather_counts_counts_emojis_in_content(clazz, guild, text_channel, make_emoji, make_message):
    duck = make_emoji(1, "duck")
    dance = make_emoji(2, "dance", animated=True)
    guild.emojis = [duck, dance]
    guild.text_channels = [readable(text_channel, [make_message(f"{duck} {duck} {dance}"), make_message("no emoji here")])]
    counts = await clazz.gather_counts(guild, 90)
    assert counts == {duck: 2, dance: 1}


async def test_gather_counts_ignores_unicode_and_foreign_emojis(clazz, guild, text_channel, make_emoji, make_message, make_reaction):
    duck = make_emoji(1, "duck")
    other_guild = make_emoji(99, "elsewhere")
    guild.emojis = [duck]
    message = make_message(f":duck: \N{DUCK} {other_guild}", reactions=[make_reaction("\N{DUCK}"), make_reaction(other_guild)])
    guild.text_channels = [readable(text_channel, [message])]
    counts = await clazz.gather_counts(guild, 90)
    assert counts == {duck: 0}


async def test_gather_counts_counts_reactions(clazz, guild, text_channel, make_emoji, make_message, make_reaction):
    duck = make_emoji(1, "duck")
    guild.emojis = [duck]
    guild.text_channels = [readable(text_channel, [make_message(reactions=[make_reaction(duck, count=3)])])]
    counts = await clazz.gather_counts(guild, 90)
    assert counts == {duck: 3}


async def test_gather_counts_scans_active_and_archived_threads(clazz, guild, text_channel, thread, autospec, make_emoji, make_message):
    duck = make_emoji(1, "duck")
    guild.emojis = [duck]
    archived = readable(autospec.of(discord.Thread), [make_message(str(duck))])
    readable(text_channel, [make_message(str(duck))])
    text_channel.threads = [readable(thread, [make_message(str(duck))])]
    text_channel.archived_threads.return_value = list_as_async_generator([archived])
    guild.text_channels = [text_channel]
    counts = await clazz.gather_counts(guild, 90)
    assert counts == {duck: 3}


async def test_gather_counts_skips_forbidden_channels(clazz, guild, text_channel, make_emoji):
    duck = make_emoji(1, "duck")
    guild.emojis = [duck]
    readable(text_channel, [])
    text_channel.history.side_effect = Forbidden(mock.Mock(status=403), "no")
    guild.text_channels = [text_channel]
    assert await clazz.gather_counts(guild, 90) == {duck: 0}


def test_report_ranks_most_used_first(clazz, make_emoji):
    duck, dance, dead = make_emoji(1, "duck"), make_emoji(2, "dance"), make_emoji(3, "dead")
    embed = clazz.report({duck: 2, dead: 0, dance: 9}, 30)
    assert embed == Embed(title="Emoji Usage \N{MIDDLE DOT} last 30 days", description=f"{dance} 9\n{duck} 2\n{dead} 0")
