import pytest
import mock
import datetime
from asyncio import CancelledError
from tests.duckmock.discord import MockAsyncIterator
from duckbot.cogs.insights import Insights
from tests.duckmock.datetime import patch_utcnow


@pytest.fixture
def setup_general_channel(bot, guild, channel):
    bot.get_all_channels.return_value = [channel]
    guild.name = "Friends Chat"
    channel.guild = guild
    channel.name = "general"


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
async def test_check_should_respond_no_messages(bot, channel, setup_general_channel):
    channel.history.return_value = MockAsyncIterator(None)
    clazz = Insights(bot)
    await clazz._Insights__check_should_respond()
    channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_check_should_respond_new_message(bot, channel, message, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=38)
        message.author.id = 244629273191645184
        channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_check_should_respond_not_special_user(bot, channel, message, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00)
        message.author.id = 0
        channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_check_should_respond_old_message_sent_by_special_user(bot, channel, message, setup_general_channel):
    with patch_utcnow(datetime.datetime(2000, 1, 1, hour=12, minute=00)):
        message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00)
        message.author.id = 244629273191645184
        channel.history.return_value = MockAsyncIterator(message)
        clazz = Insights(bot)
        await clazz._Insights__check_should_respond()
        channel.send.assert_called()


@pytest.mark.asyncio
async def test_insight_command_sends_message(bot, context):
    clazz = Insights(bot)
    await clazz._Insights__insight(context)
    context.send.assert_called()
