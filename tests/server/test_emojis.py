import pytest
import mock
from async_mock_ext import patch_async_mock
from server.emojis import Emojis


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.Emoji")
async def test_get_emoji_emoji_exists(bot, guild, emoji):
    setup_mocks(bot, guild, emoji)
    clazz = Emojis(bot, start_tasks=False)
    clazz._Emojis__refresh()
    assert clazz.get_emoji(emoji.id) == emoji


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.Emoji")
async def test_get_emoji_not_exists(bot, guild, emoji):
    setup_mocks(bot, guild, emoji)
    clazz = Emojis(bot, start_tasks=False)
    clazz._Emojis__refresh()
    with pytest.raises(KeyError):
        clazz.get_emoji(emoji.id + 1)


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.Emoji")
async def test_get_emoji_by_name_matches(bot, guild, emoji):
    setup_mocks(bot, guild, emoji)
    clazz = Emojis(bot, start_tasks=False)
    clazz._Emojis__refresh()
    assert clazz.get_emoji_by_name(emoji.name) == emoji


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.Emoji")
async def test_get_emoji_by_name_not_exists(bot, guild, emoji):
    setup_mocks(bot, guild, emoji)
    clazz = Emojis(bot, start_tasks=False)
    clazz._Emojis__refresh()
    with pytest.raises(StopIteration):
        clazz.get_emoji_by_name(emoji.name + "dead")


def setup_mocks(bot, guild, emoji):
    bot.guilds = [guild]
    guild.id = 1
    guild.emojis = [emoji]
    emoji.id = 1
    emoji.name = "tito"
