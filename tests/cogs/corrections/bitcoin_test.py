import pytest

from duckbot.cogs.corrections import Bitcoin


async def test_correct_bitcoin_bot_author(bot, message):
    message.author = bot.user
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["bitcoin", "BITCOIN", "BiTcOiN"])
async def test_correct_bitcoin_message_is_bitcoin(bot, message, text):
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_called_once_with("Magic Beans*")


@pytest.mark.parametrize("text", [" BiTcOiN   broooooooo!!!....:??", "bitcoin, brother"])
async def test_correct_bitcoin_message_contains_bitcoin(bot, message, text):
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_called_once_with("Magic Beans*")


@pytest.mark.parametrize("text", ["bit coin", "dogecoin", "hi"])
async def test_correct_bitcoin_message_is_not_bitcoin(bot, message, text):
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_not_called()
