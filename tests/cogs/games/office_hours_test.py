from unittest import mock

import pytest
import requests

from duckbot.cogs.games import OfficeHours


@mock.patch("requests.Response")
def response(r, content: str) -> requests.Response:
    r.content = content.encode()
    return r


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
@mock.patch("requests.get", return_value=response("isLiveBroadcast"))
async def test_check_if_streaming_stream_started(get, bot, general_channel):
    clazz = OfficeHours(bot)
    clazz.streaming = False
    await clazz.check_if_streaming()
    general_channel.send.assert_called_once_with("Office Hours have started!\nhttps://www.twitch.tv/conlabx")
    assert clazz.streaming


@pytest.mark.asyncio
@mock.patch("requests.get", return_value="isLiveBroadcast")
async def test_check_if_streaming_stream_ongoing(get, bot, general_channel):
    clazz = OfficeHours(bot)
    clazz.streaming = True
    await clazz.check_if_streaming()
    general_channel.send.assert_not_called()
    assert clazz.streaming
