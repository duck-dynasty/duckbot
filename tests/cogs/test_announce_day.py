import pytest
import mock
import datetime
from async_mock_ext import patch_async_mock
import cogs.channels as channels
from cogs.announce_day import AnnounceDay

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
async def test_on_hour_7am_eastern(bot, channel):
    dt = mock.Mock(wraps = datetime.datetime)
    dt.now.return_value = datetime.datetime(2002, 1, 1, hour = 7)
    with mock.patch('datetime.datetime', new = dt):
        bot.get_channel.return_value = channel
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        bot.get_channel.assert_called_once_with(channels.GENERAL)
        channel.send.assert_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
async def test_on_hour_not_7am(bot, channel):
    dt = mock.Mock(wraps = datetime.datetime)
    dt.now.return_value = datetime.datetime(2002, 1, 1, hour = 8)
    with mock.patch('datetime.datetime', new = dt):
        bot.get_channel.return_value = channel
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        bot.get_channel.assert_not_called()
        channel.send.assert_not_called()
