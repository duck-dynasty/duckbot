import pytest
import mock
from duckbot.server import Channels


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_channel_channel_exists(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    assert clazz.get_channel(channel.id) == channel


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_channel_not_exists(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    with pytest.raises(KeyError):
        clazz.get_channel(channel.id + 1)


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_channel_by_name_matches(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    assert clazz.get_channel_by_name(channel.name) == channel


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_channel_by_name_not_exists(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    with pytest.raises(StopIteration):
        clazz.get_channel_by_name(channel.name + "dead")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_general_channel_exists(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    assert clazz.get_general_channel() == channel


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Guild")
@mock.patch("discord.TextChannel")
async def test_get_general_channel_not_exists(bot, guild, channel):
    setup_mocks(bot, guild, channel)
    channel.name = "not general"
    clazz = Channels(bot, start_tasks=False)
    clazz._Channels__refresh()
    with pytest.raises(StopIteration):
        clazz.get_general_channel()


def setup_mocks(bot, guild, channel):
    bot.guilds = [guild]
    guild.id = 1
    guild.channels = [channel]
    channel.id = 1
    channel.name = "general"
