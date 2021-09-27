import asyncio
from unittest import mock

import pytest
from discord.ext.commands import CommandError

from duckbot.cogs.audio import WhoCanItBeNow
from tests.async_mock_ext import async_value


def play(*args, **kwargs):
    kwargs.get("after")(None)


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.PCMVolumeTransformer", autospec=True)
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.FFmpegPCMAudio", autospec=True)
async def test_task_loop_once(ffmpeg, vol, bot_spy, context, voice_client, skip_if_private_channel):
    context.voice_client = None
    context.author.voice.channel.connect.return_value = async_value(voice_client)
    voice_client.play.side_effect = play
    clazz = WhoCanItBeNow(bot_spy)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client is not None
    await clazz.start(context)
    assert clazz.audio_task is not None
    assert clazz.streaming is True
    await clazz.stream.wait()
    await clazz.stop(context)
    assert clazz.streaming is False
    assert clazz.audio_task is None
    assert clazz.voice_client is None


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.PCMVolumeTransformer", autospec=True)
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.FFmpegPCMAudio", autospec=True)
async def test_task_loop_repeats(ffmpeg, vol, bot_spy, context, voice_client, skip_if_private_channel):
    context.voice_client = None
    context.author.voice.channel.connect.return_value = async_value(voice_client)

    def loop_first(*args, **kwargs):
        voice_client.play.side_effect = play
        play(*args, **kwargs)

    voice_client.play.side_effect = loop_first
    clazz = WhoCanItBeNow(bot_spy)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client is not None
    await clazz.start(context)
    assert clazz.audio_task is not None
    assert clazz.streaming is True
    await clazz.stream.wait()
    await asyncio.sleep(0)
    await clazz.stream.wait()
    await clazz.stop(context)
    assert clazz.streaming is False
    assert clazz.audio_task is None
    assert clazz.voice_client is None


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.PCMVolumeTransformer", autospec=True)
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.FFmpegPCMAudio", autospec=True)
async def test_task_loop_repeats_max_times(ffmpeg, vol, bot_spy, context, voice_client, skip_if_private_channel):
    context.voice_client = None
    context.author.voice.channel.connect.return_value = async_value(voice_client)
    voice_client.play.side_effect = play
    clazz = WhoCanItBeNow(bot_spy)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client is not None
    await clazz.start(context)
    assert clazz.audio_task is not None
    assert clazz.streaming is True
    for i in range(76):
        await clazz.stream.wait()
        await asyncio.sleep(0)
        assert clazz.streaming is (i < 75)  # should be streaming 75 times only
    # stop() is called after song is played 75 times
    assert clazz.audio_task is None
    assert clazz.voice_client is None


@pytest.mark.asyncio
async def test_connect_to_voice_no_voice(bot, context):
    context.voice_client = None
    delattr(context.author, "voice")
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    context.send.assert_called_once_with("Music can only be played in a discord server, not a private channel.", delete_after=30)


@pytest.mark.asyncio
async def test_connect_to_voice_author_in_channel(bot, context, voice_client, skip_if_private_channel):
    context.voice_client = None
    context.author.voice.channel.connect.return_value = async_value(voice_client)
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client == voice_client


@pytest.mark.asyncio
async def test_connect_to_voice_author_not_in_channel(bot, context):
    context.voice_client = None
    context.author.voice = None
    clazz = WhoCanItBeNow(bot)
    with pytest.raises(CommandError):
        await clazz.connect_to_voice(context)
    context.send.assert_called_once_with("Connect to a voice channel so I know where to `!start`.", delete_after=30)


@pytest.mark.asyncio
async def test_connect_to_voice_already_connected(bot, context, voice_client):
    context.voice_client = voice_client
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    voice_client.stop.assert_called()


@pytest.mark.asyncio
async def test_start_already_started(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    await clazz.start(context)
    bot.loop.create_task.assert_not_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.PCMVolumeTransformer", autospec=True)
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.FFmpegPCMAudio", autospec=True)
async def test_stop_disconnects(ffmpeg, vol, bot, context, voice_client):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    clazz.audio_task = asyncio.create_task(clazz.stream_audio())
    clazz.voice_client = voice_client
    await clazz.stop(context)
    voice_client.disconnect.assert_called()
    assert clazz.voice_client is None
    assert clazz.audio_task is None
    assert clazz.streaming is False


@pytest.mark.asyncio
async def test_stop_not_streaming(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = False
    await clazz.stop(context)
    context.send.assert_called_once_with("Brother, no :musical_note: :saxophone: is active.", delete_after=30)


@pytest.mark.asyncio
async def test_stop_null_context_not_streaming(bot):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = False
    await clazz.stop()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.PCMVolumeTransformer", autospec=True)
@mock.patch("duckbot.cogs.audio.who_can_it_be_now.FFmpegPCMAudio", autospec=True)
async def test_cog_unload_stops_streaming(ffmpeg, vol, bot, voice_client):
    bot.loop = asyncio.get_event_loop()
    clazz = WhoCanItBeNow(bot)
    clazz.voice_client = voice_client
    clazz.audio_task = bot.loop.create_task(clazz.stream_audio())
    clazz.streaming = True
    task = clazz.cog_unload()
    await task
    assert clazz.streaming is False
    assert clazz.voice_client is None
    assert clazz.audio_task is None


@pytest.mark.asyncio
async def test_delete_command_message(bot, context):
    clazz = WhoCanItBeNow(bot)
    await clazz.delete_command_message(context)
    context.message.delete.assert_called()
