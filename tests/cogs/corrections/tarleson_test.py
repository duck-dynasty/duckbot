import pytest

from duckbot.cogs.corrections import Tarleson


@pytest.mark.asyncio
async def test_correct_tarleson_bot_author(bot, message):
    message.author = bot.user
    clazz = Tarleson(bot)
    await clazz.correct_tarleson(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["Tucker Carleson", "tucker carleson", "TUCKER CARLESON", "TuCkEr CaRlEsOn"])
async def test_correct_tarleson_message_is_tucker_carleson(bot, message, text):
    message.content = text
    clazz = Tarleson(bot)
    await clazz.correct_tarleson(message)
    message.channel.send.assert_called_once_with("I believe it is pronounced cucker tarleson")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["Tucker Carleson is lameo", "bro, Tucker Carleson tans his ballz"])
async def test_correct_tarleson_message_contains_tucker_carleson(bot, message, text):
    message.content = text
    clazz = Tarleson(bot)
    await clazz.correct_tarleson(message)
    message.channel.send.assert_called_once_with("I believe it is pronounced cucker tarleson")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["tuck the cuck", "cucker tarleson", "hello tuck ercarle son"])
async def test_correct_tarleson_message_is_not_tucker_carleson(bot, message, text):
    message.content = text
    clazz = Tarleson(bot)
    await clazz.correct_tarleson(message)
    message.channel.send.assert_not_called()
