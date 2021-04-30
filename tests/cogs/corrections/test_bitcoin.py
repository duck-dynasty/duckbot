import pytest
from duckbot.cogs.corrections import Bitcoin


@pytest.mark.asyncio
async def test_correct_bitcoin_bot_author(bot, message):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["bitcoin", "BITCOIN", "BiTcOiN"])
async def test_correct_bitcoin_message_is_bitcoin(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_called_once_with("Magic Beans*")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [" BiTcOiN   broooooooo!!!....:??", "bitcoin, brother"])
async def test_correct_bitcoin_message_contains_bitcoin(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_called_once_with("Magic Beans*")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["bit coin", "dogecoin", "hi"])
async def test_correct_bitcoin_message_is_not_bitcoin(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Bitcoin(bot)
    await clazz.correct_bitcoin(message)
    message.channel.send.assert_not_called()
