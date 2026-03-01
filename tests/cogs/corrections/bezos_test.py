import pytest

from duckbot.cogs.corrections import Bezos


async def test_correct_bezos_bot_author(bot_message):
    bot_message.content = "bezo"
    clazz = Bezos()
    await clazz.correct_bezos(bot_message)
    bot_message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["Jeffrey Bezos", "fekin bezo at it again"])
async def test_correct_bezos_message_contains_bezos(message, text):
    message.content = text
    clazz = Bezos()
    await clazz.correct_bezos(message)
    message.channel.send.assert_called_once_with("There is no Jeff, only Andy.")


@pytest.mark.parametrize("text", ["andy is the new jeff"])
async def test_correct_bezos_message_is_not_bezos(message, text):
    message.content = text
    clazz = Bezos()
    await clazz.correct_bezos(message)
    message.channel.send.assert_not_called()
