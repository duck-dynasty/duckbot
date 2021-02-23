import pytest
import mock
import datetime
from async_mock_ext import patch_async_mock
import server.channels as channels
from cogs.announce_day import AnnounceDay
from duckmock.datetime import patch_now

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
async def test_on_hour_7am_eastern(bot, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour = 7)):
        bot.get_channel.return_value = channel
        clazz = AnnounceDay(bot, start_tasks=False)
        await clazz._AnnounceDay__on_hour()
        bot.get_channel.assert_called_once_with(channels.GENERAL)
        channel.send.assert_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('discord.TextChannel')
async def test_on_hour_not_7am(bot, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour = 8)):
        bot.get_channel.return_value = channel
        clazz = AnnounceDay(bot, start_tasks=False)
        await clazz._AnnounceDay__on_hour()
        bot.get_channel.assert_not_called()
        channel.send.assert_not_called()
