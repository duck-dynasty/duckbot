import pytest
import mock
from duckbot.cogs import WhoCanItBeNow


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_start_creates_task(bot, context):
    clazz = WhoCanItBeNow(bot)
    await clazz._WhoCanItBeNow__start(context)
    assert clazz.player is not None
    assert clazz.streaming is True

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
@mock.patch("duckbot.server.Channels")
@mock.patch("discord.VoiceChannel")
@mock.patch("discord.VoiceClient")
async def test_stream_audio_loops_song(bot, channels, channel, client):
    bot.get_cog.return_value = channels 
    channels.get_channel_by_name.return_value = channel
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    await clazz.stream_audio()
    channels.get_channel_by_name.assert_called_once_with("Hangout 1")
