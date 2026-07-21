import datetime
from unittest import mock

import discord
import pytest

from duckbot.cogs.insights import Memes
from tests import list_as_async_generator
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz(bot) -> Memes:
    return bind_commands(Memes(bot))


@pytest.fixture
def memes_channel(bot, guild, text_channel) -> discord.TextChannel:
    bot.get_all_channels.return_value = [text_channel]
    guild.name = "Friends Chat"
    text_channel.guild = guild
    text_channel.name = "toms-memes"
    text_channel.created_at = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    return text_channel


@pytest.fixture
def attachment(autospec) -> discord.Attachment:
    a = autospec.of(discord.Attachment)
    a.url = "https://cdn.discordapp.com/attachments/meme.png"
    return a


async def test_meme_sends_attachment_url(clazz, context, memes_channel, raw_message, attachment):
    raw_message.attachments = [attachment]
    memes_channel.history.return_value = list_as_async_generator([raw_message])
    await clazz.meme(context)
    context.send.assert_called_once_with(attachment.url)


async def test_meme_no_channel(clazz, bot, context):
    bot.get_all_channels.return_value = []
    await clazz.meme(context)
    context.send.assert_called_once_with("https://tenor.com/view/gnocchi-soup-gif-27425983")


async def test_meme_no_attachments_in_any_window(clazz, context, memes_channel, raw_message):
    raw_message.attachments = []
    memes_channel.history.side_effect = lambda **kwargs: list_as_async_generator([raw_message])
    await clazz.meme(context)
    context.send.assert_called_once_with("https://tenor.com/view/gnocchi-soup-gif-27425983")


async def test_meme_retries_until_attachment_found(clazz, context, memes_channel, raw_message, attachment):
    meme = mock.Mock(spec=discord.Message)
    meme.attachments = [attachment]
    raw_message.attachments = []
    windows = iter([[raw_message], [raw_message], [meme]])
    memes_channel.history.side_effect = lambda **kwargs: list_as_async_generator(next(windows))
    await clazz.meme(context)
    context.send.assert_called_once_with(attachment.url)
    assert memes_channel.history.call_count == 3


@mock.patch("random.choice")
async def test_random_attachment_picks_from_messages_with_attachments(choice, clazz, memes_channel, raw_message, attachment):
    other = mock.Mock(spec=discord.Message)
    other.attachments = []
    raw_message.attachments = [attachment]
    memes_channel.history.return_value = list_as_async_generator([other, raw_message])
    choice.side_effect = lambda options: options[0]
    assert await clazz.random_attachment(memes_channel) == attachment.url
    choice.assert_has_calls([mock.call([raw_message]), mock.call([attachment])])


@mock.patch("random.uniform", return_value=60.0)
@mock.patch("duckbot.cogs.insights.memes.utcnow", return_value=datetime.datetime(2000, 1, 2, tzinfo=datetime.timezone.utc))
def test_random_time_is_between_creation_and_now(utcnow, uniform, clazz, memes_channel):
    assert clazz.random_time(memes_channel) == datetime.datetime(2000, 1, 1, minute=1, tzinfo=datetime.timezone.utc)
    uniform.assert_called_once_with(0, 86400.0)
