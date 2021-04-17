import pytest
import mock
import asyncio
from tests.async_mock_ext import async_value
from duckbot.cogs import WhoCanItBeNow


def play(*args, **kwargs):
    kwargs.get("after")(None)


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("duckbot.server.Channels")
@mock.patch("discord.VoiceChannel")
@mock.patch("discord.VoiceClient")
async def test_task_loop(bot, context, channels, voice, client):
    bot.get_cog.return_value = channels
    channels.get_channel_by_name.return_value = voice
    voice.connect.return_value = async_value(client)
    client.play = play
    clazz = WhoCanItBeNow(bot)
    await clazz._WhoCanItBeNow__start(context)
    assert clazz.player is not None
    assert clazz.streaming is True
    await clazz.stream.wait()
    await clazz._WhoCanItBeNow__stop(context)
    assert clazz.streaming is False
    assert clazz.player is None
    assert clazz.client is None


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_start_already_started(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    await clazz._WhoCanItBeNow__start(context)
    context.send.assert_called_once_with("Already streaming, you fool!")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("discord.VoiceClient")
async def test_stop_disconnects(bot, context, client):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    clazz.player = asyncio.create_task(clazz.stream_audio())
    clazz.client = client
    await clazz._WhoCanItBeNow__stop(context)
    client.disconnect.assert_called()
    assert clazz.client is None
    assert clazz.streaming is False


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_stop_not_streaming(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = False
    await clazz._WhoCanItBeNow__stop(context)
    context.send.assert_called_once_with("Nothing to stop, you fool!")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
async def test_stop_if_running_stops_streaming(bot):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    await clazz.stop_if_running()
    assert clazz.streaming is False
