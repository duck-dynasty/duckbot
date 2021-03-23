import pytest
import mock
import datetime
from duckbot.cogs import AnnounceDay
from tests.duckmock.datetime import patch_now


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("duckbot.server.Channels")
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
@mock.patch("discord.ext.commands.Bot")
@mock.patch("duckbot.server.Channels")
@mock.patch("discord.TextChannel")
async def test_on_hour_not_7am(bot, channels, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour=8)):
        bot.get_cog.return_value = channels
        channels.get_general_channel.return_value = channel
        clazz = AnnounceDay(bot, start_tasks=False)
        await clazz._AnnounceDay__on_hour()
        channels.get_general_channel.assert_not_called()
        channel.send.assert_not_called()
