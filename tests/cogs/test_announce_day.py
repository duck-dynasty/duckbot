import pytest
import mock
import datetime
from async_mock_ext import patch_async_mock
from cogs.announce_day import AnnounceDay
from duckmock.datetime import patch_now


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("server.channels")
@mock.patch("discord.TextChannel")
async def test_on_hour_7am_eastern(bot, channels, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour=7)):
        bot.get_cog.return_value = channels
        channels.get_general_channel.return_value = channel
        clazz = AnnounceDay(bot, start_tasks=False)
        await clazz._AnnounceDay__on_hour()
        channels.get_general_channel.assert_called()
        channel.send.assert_called()


@pytest.mark.asyncio
@patch_async_mock
@mock.patch("discord.ext.commands.Bot")
@mock.patch("server.channels")
@mock.patch("discord.TextChannel")
async def test_on_hour_not_7am(bot, channels, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour=8)):
        bot.get_cog.return_value = channels
        channels.get_general_channel.return_value = channel
        clazz = AnnounceDay(bot, start_tasks=False)
        await clazz._AnnounceDay__on_hour()
        channels.get_general_channel.assert_not_called()
        channel.send.assert_not_called()
