import pytest

from duckbot.cogs.shrug import Shrug


async def test_shrug_sends_shrug(bot, context):
    clazz = Shrug(bot)
    await clazz.shrug(context)
    context.send.assert_called_once_with("¯\_(ツ)_/¯")
