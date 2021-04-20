import pytest
import mock
import asyncio
from tests.async_mock_ext import async_value
from discord.ext.commands import CommandError
from duckbot.cogs import WhoCanItBeNow


def play(*args, **kwargs):
    kwargs.get("after")(None)


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("discord.VoiceChannel")
@mock.patch("discord.VoiceClient")
async def test_task_loop(bot, context, voice, client):
    bot.loop = asyncio.get_event_loop()
    context.voice_client = None
    context.author.voice = voice
    voice.channel.connect.return_value = async_value(client)
    client.play = play
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client is not None
    await clazz._WhoCanItBeNow__start(context)
    assert clazz.audio_task is not None
    assert clazz.streaming is True
    await clazz.stream.wait()
    await clazz._WhoCanItBeNow__stop(context)
    assert clazz.streaming is False
    assert clazz.audio_task is None
    assert clazz.voice_client is None


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("discord.VoiceClient")
async def test_connect_to_voice_author_in_channel(bot, context, client):
    context.voice_client = None
    context.author.voice.channel.connect.return_value = async_value(client)
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    assert clazz.voice_client == client


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_connect_to_voice_author_not_in_channel(bot, context):
    context.voice_client = None
    context.author.voice = None
    clazz = WhoCanItBeNow(bot)
    with pytest.raises(CommandError):
        await clazz.connect_to_voice(context)
    context.send.assert_called_once_with("Connect to a voice channel so I know where to `!start`.")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("discord.VoiceClient")
async def test_connect_to_voice_already_connected(bot, context, client):
    context.voice_client = client
    clazz = WhoCanItBeNow(bot)
    await clazz.connect_to_voice(context)
    client.stop.assert_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_start_already_started(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    await clazz._WhoCanItBeNow__start(context)
    bot.loop.create_task.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
@mock.patch("discord.VoiceClient")
async def test_stop_disconnects(bot, context, voice_client):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = True
    clazz.audio_task = asyncio.create_task(clazz.stream_audio())
    clazz.voice_client = voice_client
    await clazz._WhoCanItBeNow__stop(context)
    voice_client.disconnect.assert_called()
    assert clazz.voice_client is None
    assert clazz.audio_task is None
    assert clazz.streaming is False


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.commands.Context")
async def test_stop_not_streaming(bot, context):
    clazz = WhoCanItBeNow(bot)
    clazz.streaming = False
    await clazz._WhoCanItBeNow__stop(context)
    context.send.assert_called_once_with("Brother, no :musical_note: :saxophone: is active.")


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.VoiceClient")
async def test_cog_unload_stops_streaming(bot, voice_client):
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
