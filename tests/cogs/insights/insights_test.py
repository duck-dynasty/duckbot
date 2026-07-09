import datetime
from unittest import mock

import pytest

from duckbot.cogs.insights import Insights
from tests import list_as_async_generator
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz(bot) -> Insights:
    return bind_commands(Insights(bot))


async def test_before_loop_waits_for_bot(clazz, bot):
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


async def test_cog_unload_cancels_task(clazz):
    clazz.cog_unload()
    clazz.check_should_respond_loop.cancel.assert_called()


async def test_check_should_respond_no_history(clazz, general_channel):
    general_channel.history.return_value = list_as_async_generator([])
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_new_message(utcnow, clazz, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=38, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 244629273191645184
    general_channel.history.return_value = list_as_async_generator([raw_message])
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_not_special_user(utcnow, clazz, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 0
    general_channel.history.return_value = list_as_async_generator([raw_message])
    await clazz.check_should_respond()
    general_channel.send.assert_not_called()


@mock.patch("duckbot.cogs.insights.insights.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_check_should_respond_old_message_sent_by_special_user(utcnow, clazz, raw_message, general_channel):
    raw_message.created_at = datetime.datetime(2000, 1, 1, hour=11, minute=00, tzinfo=datetime.timezone.utc)
    raw_message.author.id = 244629273191645184
    general_channel.history.return_value = list_as_async_generator([raw_message])
    await clazz.check_should_respond()
    general_channel.send.assert_called()


async def test_insight_sends_message(clazz, context):
    await clazz.insight(context)
    context.send.assert_called()
