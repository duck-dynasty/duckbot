import pytest

from duckbot.cogs.corrections import Tarlson


async def test_correct_tarlson_bot_author(bot, message):
    message.author = bot.user
    clazz = Tarlson(bot)
    await clazz.correct_tarlson(message)
    message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["Tucker Carlson", "tucker carlson", "TUCKER CARLSON", "TuCkEr CaRlSon"])
async def test_correct_tarlson_message_is_tucker_carlson(bot, message, text):
    message.content = text
    clazz = Tarlson(bot)
    await clazz.correct_tarlson(message)
    message.channel.send.assert_called_once_with("I believe it is pronounced cucker tarlson")


@pytest.mark.parametrize("text", ["Tucker Carlson is lameo", "bro, Tucker Carlson tans his ballz"])
async def test_correct_tarlson_message_contains_tucker_carlson(bot, message, text):
    message.content = text
    clazz = Tarlson(bot)
    await clazz.correct_tarlson(message)
    message.channel.send.assert_called_once_with("I believe it is pronounced cucker tarlson")


@pytest.mark.parametrize("text", ["tuck the cuck", "cucker tarlson", "hello tuck ercarl son"])
async def test_correct_tarlson_message_is_not_tucker_carlson(bot, message, text):
    message.content = text
    clazz = Tarlson(bot)
    await clazz.correct_tarlson(message)
    message.channel.send.assert_not_called()
