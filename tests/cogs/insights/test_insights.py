import pytest
from unittest import mock
import datetime
from discord import ChannelType
from asyncio import CancelledError
from tests.duckmock.discord import MockAsyncIterator
from duckbot.cogs.insights import Insights
from tests.duckmock.datetime import patch_utcnow


@pytest.fixture
def setup_general_channel(bot, guild, text_channel):
    bot.get_all_channels.return_value = [text_channel]
    guild.name = "Friends Chat"
    text_channel.guild = guild
    text_channel.name = "general"


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot):
    clazz = Insights(bot)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot):
    clazz = Insights(bot)
    clazz.cog_unload()
    with pytest.raises(CancelledError):
        await clazz.check_should_respond.get_task()
    assert not clazz.check_should_respond.is_running()


@pytest.mark.asyncio
async def test_check_should_respond_no_history(bot, guild, guild_channel):
    bot.get_all_channels.return_value = [guild_channel]
    guild.name = "Friends Chat"
    guild_channel.guild = guild
    guild_channel.name = "general"
    if guild_channel.type == ChannelType.text:
        guild_channel.history.return_value = MockAsyncIterator(None)
    clazz = Insights(bot)
    await clazz._Insights__check_should_respond()
    if guild_channel.type == ChannelType.text:
        guild_channel.send.assert_not_called()
    else:
        assert not guild_channel.method_calls


@pytest.mark.asyncio
@mock.patch("discord.Message", autospec=True)
async def test_check_should_respond_new_message(message, bot, text_channel, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=38)
        message.author.id = 244629273191645184
        text_channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        text_channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message", autospec=True)
async def test_check_should_respond_not_special_user(message, bot, text_channel, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00)
        message.author.id = 0
        text_channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        text_channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message", autospec=True)
async def test_check_should_respond_old_message_sent_by_special_user(message, bot, text_channel, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00)
        message.author.id = 244629273191645184
        text_channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        text_channel.send.assert_called()


@pytest.mark.asyncio
async def test_insight_command_sends_message(bot, context):
    clazz = Insights(bot)
    await clazz._Insights__insight(context)
    context.send.assert_called()
