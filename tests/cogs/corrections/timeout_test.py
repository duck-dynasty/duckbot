from unittest import mock
import discord
from duckbot.cogs.corrections import Timeout
from duckbot.cogs.corrections.timeout import TIMEOUT_SECONDS

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


@mock.patch("duckbot.cogs.corrections.timeout.asyncio.sleep")
async def test_timeout_yelling_message(sleep, bot, message):
    message.content = "HELLO THIS IS YELLING"
    message.author = mock.MagicMock(spec=discord.Member)
    message.author.bot = False
    clazz = Timeout(bot)
    await clazz.timeout_yellers(message)
    message.reply.assert_called_once()
    sleep.assert_called_once_with(TIMEOUT_SECONDS)

async def test_is_yelling_all_caps(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("HELLO THIS IS YELLING") is True


async def test_is_yelling_lowercase(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("hello this is not yelling") is False


async def test_is_yelling_short_message(bot):
    clazz = Timeout(bot)
    assert clazz.is_yelling("HI") is False

@mock.patch("duckbot.cogs.corrections.timeout.asyncio.sleep")
async def test_timeout_no_timeout_in_dm(sleep, bot, message):
    message.content = "HELLO THIS IS YELLING"
    message.author = mock.MagicMock(spec=discord.User)
    message.author.bot = False
    clazz = Timeout(bot)
    await clazz.timeout_yellers(message)
    message.reply.assert_not_called()
    sleep.assert_not_called()