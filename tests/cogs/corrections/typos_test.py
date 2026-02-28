from unittest import mock

from textblob import TextBlob

from duckbot.cogs.corrections import Typos
from tests import list_as_async_generator


async def test_correct_typos_bot_user(bot, message):
    bot.user = message.author
    clazz = Typos()
    await clazz.correct_typos(message)
    message.channel.history.assert_not_called()


async def test_correct_typos_message_is_not_fuck(bot, message):
    message.content = "poopy"
    clazz = Typos()
    await clazz.correct_typos(message)
    message.channel.history.assert_not_called()


async def test_correct_typos_no_previous_message(bot, message):
    message.content = "fuck"
    message.channel.history.return_value = list_as_async_generator([])
    clazz = Typos()
    await clazz.correct_typos(message)
    message.reply.assert_not_called()


@mock.patch("discord.Message")
@mock.patch("textblob.TextBlob")
async def test_correct_typos_no_typos_in_previous(textblob, prev_message, bot, message):
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "hello"
    message.channel.history.return_value = list_as_async_generator([prev_message])
    textblob.return_value.correct.return_value = TextBlob(prev_message.content)
    clazz = Typos()
    await clazz.correct_typos(message)
    message.reply.assert_called_once_with(f"There's no need for harsh words, {message.author.display_name}.")


@mock.patch("discord.Message")
@mock.patch("textblob.TextBlob")
async def test_correct_typos_sends_correction(textblob, prev_message, bot, message):
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "henlo"
    message.channel.history.return_value = list_as_async_generator([prev_message])
    textblob.return_value.correct.return_value = TextBlob("hello")
    clazz = Typos()
    await clazz.correct_typos(message)
    prev_message.reply.assert_called_once_with(f"> hello\nI fixed it, {message.author.display_name}. :microphone: :wave:")
