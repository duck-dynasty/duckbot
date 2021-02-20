import pytest
import mock
import datetime
from async_mock_ext import patch_async_mock
import server.channels as channels
from cogs.insights import Insights

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
async def test_check_should_respond_no_messages(bot, channel):
    bot.get_channel.return_value = channel
    channel.history.return_value = Hist(None)
    clazz = Insights(bot, start_tasks=False)
    await clazz._Insights__check_should_respond()
    bot.get_channel.assert_called_once_with(channels.GENERAL)
    channel.send.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
@mock.patch('discord.Message')
async def test_check_should_respond_new_message(bot, channel, message):
    dt = mock.Mock(wraps = datetime.datetime)
    dt.utcnow.return_value = datetime.datetime(2000, 1, 1, hour = 12, minute = 00)
    with mock.patch('datetime.datetime', new = dt):
        bot.get_channel.return_value = channel
        message.created_at = datetime.datetime(2000, 1, 1, hour = 11, minute = 38)
        message.author.id = 244629273191645184
        channel.history.return_value = Hist(message)
        clazz = Insights(bot, start_tasks=False)
        await clazz._Insights__check_should_respond()
        bot.get_channel.assert_called_once_with(channels.GENERAL)
        channel.send.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
@mock.patch('discord.Message')
async def test_check_should_respond_not_special_user(bot, channel, message):
    dt = mock.Mock(wraps = datetime.datetime)
    dt.utcnow.return_value = datetime.datetime(2000, 1, 1, hour = 12, minute = 00)
    with mock.patch('datetime.datetime', new = dt):
        bot.get_channel.return_value = channel
        message.created_at = datetime.datetime(2000, 1, 1, hour = 11, minute = 00)
        message.author.id = 0
        channel.history.return_value = Hist(message)
        clazz = Insights(bot, start_tasks=False)
        await clazz._Insights__check_should_respond()
        bot.get_channel.assert_called_once_with(channels.GENERAL)
        channel.send.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
@mock.patch('discord.Message')
async def test_check_should_respond_old_message_sent_by_special_user(bot, channel, message):
    dt = mock.Mock(wraps = datetime.datetime)
    dt.utcnow.return_value = datetime.datetime(2000, 1, 1, hour = 12, minute = 00)
    with mock.patch('datetime.datetime', new = dt):
        bot.get_channel.return_value = channel
        message.created_at = datetime.datetime(2000, 1, 1, hour = 11, minute = 00)
        message.author.id = 244629273191645184
        channel.history.return_value = Hist(message)
        clazz = Insights(bot, start_tasks=False)
        await clazz._Insights__check_should_respond()
        bot.get_channel.assert_called_once_with(channels.GENERAL)
        channel.send.assert_called()

class Hist:
    def __init__(self, message):
        self.message = message
    
    async def flatten(self):
        if self.message:
            return [ self.message ]
        else:
            return []
