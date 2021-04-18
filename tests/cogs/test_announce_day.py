import pytest
import mock
import datetime
from asyncio import CancelledError
from duckbot.cogs import AnnounceDay
from tests.duckmock.datetime import patch_now


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot):
    clazz = AnnounceDay(bot)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot):
    clazz = AnnounceDay(bot)
    clazz.cog_unload()
    with pytest.raises(CancelledError):
        await clazz.on_hour.get_task()
    assert not clazz.on_hour.is_running()


@pytest.mark.asyncio
async def test_on_hour_7am_eastern(bot, guild, channel):
    with patch_now(datetime.datetime(2002, 1, 1, hour=7)):
        bot.get_all_channels.return_value = [channel]
        guild.name = "Friends Chat"
        channel.guild = guild
        channel.name = "general"
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        channel.send.assert_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("hour", [h for h in range(0, 24) if h != 7])
async def test_on_hour_not_7am(bot, hour):
    with patch_now(datetime.datetime(2002, 1, 1, hour=hour)):
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        bot.get_all_channels.assert_not_called()
