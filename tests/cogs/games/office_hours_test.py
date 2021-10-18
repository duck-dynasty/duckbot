import pytest

from duckbot.cogs.games import OfficeHours

TWITCH_URI = "https://www.twitch.tv/conlabx"


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot):
    clazz = OfficeHours(bot)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


def test_cog_unload_cancels_task(bot):
    clazz = OfficeHours(bot)
    clazz.cog_unload()
    clazz.check_if_streaming_loop.cancel.assert_called()


@pytest.mark.asyncio
async def test_check_if_streaming_stream_started(bot, responses, general_channel):
    responses.add(responses.GET, TWITCH_URI, body="isLiveBroadcast")
    clazz = OfficeHours(bot)
    clazz.streaming = False
    await clazz.check_if_streaming()
    general_channel.send.assert_called_once_with('"Office Hours" have started!\nhttps://www.twitch.tv/conlabx')
    assert clazz.streaming
    clazz.check_if_streaming_loop.change_interval.assert_called_once_with(hours=12.0)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == TWITCH_URI


@pytest.mark.asyncio
async def test_check_if_streaming_stream_ongoing(bot, responses, general_channel):
    responses.add(responses.GET, TWITCH_URI, body="isLiveBroadcast")
    clazz = OfficeHours(bot)
    clazz.streaming = True
    await clazz.check_if_streaming()
    general_channel.send.assert_not_called()
    assert clazz.streaming
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == TWITCH_URI


@pytest.mark.asyncio
async def test_check_if_streaming_stream_not_started(bot, responses, general_channel):
    responses.add(responses.GET, TWITCH_URI, body="bruh")
    clazz = OfficeHours(bot)
    clazz.streaming = False
    await clazz.check_if_streaming()
    general_channel.send.assert_not_called()
    assert not clazz.streaming
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == TWITCH_URI


@pytest.mark.asyncio
async def test_check_if_streaming_stream_stopped(bot, responses, general_channel):
    responses.add(responses.GET, TWITCH_URI, body="bruh")
    clazz = OfficeHours(bot)
    clazz.streaming = True
    await clazz.check_if_streaming()
    general_channel.send.assert_not_called()
    assert not clazz.streaming
    clazz.check_if_streaming_loop.change_interval.assert_called_once_with(minutes=15.0)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == TWITCH_URI
