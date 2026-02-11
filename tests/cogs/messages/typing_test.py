from unittest import mock

from duckbot.cogs.messages import Typing


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("random.random", return_value=0.01)
async def test_typing_response_random_fails(random, sleep, bot, text_channel, user):
    clazz = Typing(bot)
    await clazz.typing_response(text_channel, user, None)
    text_channel.typing.assert_not_called()


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("random.random", return_value=0.0001)
async def test_typing_response_random_passes(random, sleep, bot, text_channel, user):
    clazz = Typing(bot)
    await clazz.typing_response(text_channel, user, None)
    text_channel.typing.assert_called_once()


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("random.random", return_value=0)
async def test_typing_response_ignores_bot_user(random, sleep, bot, text_channel):
    clazz = Typing(bot)
    await clazz.typing_response(text_channel, bot.user, None)
    text_channel.typing.assert_not_called()
