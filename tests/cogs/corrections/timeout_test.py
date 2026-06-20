from unittest import mock
from duckbot.cogs.corrections import Timeout


async def test_timeout_bot_user(bot, bot_message):
    bot_message.content = "HELLO THIS IS YELLING"
    clazz = Timeout(bot)
    await clazz.timeout_yellers(bot_message)
    bot_message.reply.assert_not_called()


async def test_timeout_short_message(bot, message):
    message.content = "HI"
    clazz = Timeout(bot)
    await clazz.timeout_yellers(message)
    message.reply.assert_not_called()


async def test_timeout_lowercase_message(bot, message):
    message.content = "hello this is not yelling"
    clazz = Timeout(bot)
    await clazz.timeout_yellers(message)
    message.reply.assert_not_called()


async def test_timeout_yelling_message(bot, message):
    message.content = "HELLO THIS IS YELLING"
    clazz = Timeout(bot)
    await clazz.timeout_yellers(message)
    message.reply.assert_called_once()


async def test_is_yelling_all_caps(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("HELLO THIS IS YELLING") is True


async def test_is_yelling_lowercase(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("hello this is not yelling") is False


async def test_is_yelling_short_message(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("HI") is False