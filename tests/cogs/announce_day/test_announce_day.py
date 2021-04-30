import pytest
import datetime
from discord import ChannelType
from asyncio import CancelledError
from duckbot.cogs.announce_day import AnnounceDay
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
async def test_on_hour_7am_eastern_special_day(bot, guild, guild_channel):
    bot.get_all_channels.return_value = [guild_channel]
    guild.name = "Friends Chat"
    guild_channel.guild = guild
    guild_channel.name = "general"
    with patch_now(datetime.datetime(2002, 1, 1, hour=7)):
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        if guild_channel.type == ChannelType.text:
            guild_channel.send.assert_called()
        else:
            assert not guild_channel.method_calls


@pytest.mark.asyncio
async def test_on_hour_7am_eastern_not_special_day(bot, guild, guild_channel):
    bot.get_all_channels.return_value = [guild_channel]
    guild.name = "Friends Chat"
    guild_channel.guild = guild
    guild_channel.name = "general"
    with patch_now(datetime.datetime(2002, 1, 21, hour=7)):
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        if guild_channel.type == ChannelType.text:
            guild_channel.send.assert_called()
        else:
            assert not guild_channel.method_calls


@pytest.mark.asyncio
@pytest.mark.parametrize("hour", [h for h in range(0, 24) if h != 7])
async def test_on_hour_not_7am(bot, hour):
    with patch_now(datetime.datetime(2002, 1, 1, hour=hour)):
        clazz = AnnounceDay(bot)
        await clazz._AnnounceDay__on_hour()
        bot.get_all_channels.assert_not_called()
