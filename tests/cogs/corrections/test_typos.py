from unittest import mock

import pytest
from textblob import TextBlob

from duckbot.cogs.corrections import Typos
from tests.duckmock.discord import MockAsyncIterator


@pytest.mark.asyncio
async def test_correct_typos_bot_user(bot, message):
    bot.user = message.author
    clazz = Typos(bot)
    await clazz.correct_typos(message)
    message.channel.history.assert_not_called()


@pytest.mark.asyncio
async def test_correct_typos_message_is_not_fuck(bot, message):
    message.content = "poopy"
    clazz = Typos(bot)
    await clazz.correct_typos(message)
    message.channel.history.assert_not_called()


@pytest.mark.asyncio
async def test_correct_typos_no_previous_message(bot, message):
    message.content = "fuck"
    message.channel.history.return_value = MockAsyncIterator(None)
    clazz = Typos(bot)
    await clazz.correct_typos(message)
    message.reply.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("textblob.TextBlob")
async def test_correct_typos_no_typos_in_previous(textblob, prev_message, bot, message):
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "hello"
    message.channel.history.return_value = MockAsyncIterator(prev_message)
    textblob.return_value.correct.return_value = TextBlob(prev_message.content)
    clazz = Typos(bot)
    await clazz.correct_typos(message)
    message.reply.assert_called_once_with(f"There's no need for harsh words, {message.author.display_name}.")


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("textblob.TextBlob")
async def test_correct_typos_sends_correction(textblob, prev_message, bot, message):
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "henlo"
    message.channel.history.return_value = MockAsyncIterator(prev_message)
    textblob.return_value.correct.return_value = TextBlob("hello")
    clazz = Typos(bot)
    await clazz.correct_typos(message)
    prev_message.reply.assert_called_once_with(f"> hello\nThink I fixed it, {message.author.display_name}!")
