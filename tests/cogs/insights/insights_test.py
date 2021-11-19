import datetime
from unittest import mock

import pytest

from duckbot.cogs.insights import Insights
from tests.duckmock.discord import MockAsyncIterator


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot):
    clazz = Insights(bot)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot):
    clazz = Insights(bot)
    clazz.cog_unload()
    clazz.check_should_respond_loop.cancel.assert_called()


@pytest.mark.asyncio
async def test_check_should_respond_no_history(bot, general_channel):
    general_channel.history.return_value = MockAsyncIterator(None)
    clazz = Insights(bot)
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_new_message(utcnow, bot, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=38, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 244629273191645184
    general_channel.history.return_value = MockAsyncIterator(raw_message)
    clazz = Insights(bot)
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_not_special_user(utcnow, bot, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 0
    general_channel.history.return_value = MockAsyncIterator(raw_message)
    clazz = Insights(bot)
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_old_message_sent_by_special_user(utcnow, bot, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 244629273191645184
    general_channel.history.return_value = MockAsyncIterator(raw_message)
    clazz = Insights(bot)
    await clazz.check_should_respond()
    general_channel.send.assert_called()


@pytest.mark.asyncio
async def test_insight_command_sends_message(bot, context):
    clazz = Insights(bot)
    await clazz.insight(context)
    context.send.assert_called()
