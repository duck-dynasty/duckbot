from unittest import mock

import d20
import pytest

from duckbot.cogs.games import Dice
from duckbot.util.messages import MAX_MESSAGE_LENGTH


@pytest.mark.asyncio
@mock.patch("d20.Roller.roll", side_effect=[d20.RollValueError("ded")])
async def test_roll_dice_error(roller, bot, context):
    clazz = Dice(bot)
    await clazz.roll(context, "1d-20")
    context.send.assert_called_once_with("Oh... :nauseated_face: I don't feel so good... :face_vomiting:\n```ded```", delete_after=30)


@pytest.mark.asyncio
async def test_roll_dice_too_many_dice(bot, context):
    clazz = Dice(bot)
    await clazz.roll(context, "100001d20")
    context.send.assert_called_once_with("I can only roll up to 100000 dice.", delete_after=30)


@pytest.mark.asyncio
@mock.patch("d20.Roller")
async def test_roll_result_too_long_for_message(roller, bot, context):
    roller.return_value.roll.return_value.result = "x" * MAX_MESSAGE_LENGTH
    roller.return_value.roll.return_value.total = 100
    clazz = Dice(bot)
    await clazz.roll(context, "1d20")
    context.send.assert_called_once_with(f"**Rolls**: {'x' * (MAX_MESSAGE_LENGTH - 50)}...\n**Total**: 100")


@pytest.mark.asyncio
@mock.patch("d20.Roller")
async def test_roll_sends_result(roller, bot, context):
    roller.return_value.roll.return_value.result = "results"
    roller.return_value.roll.return_value.total = 1
    clazz = Dice(bot)
    await clazz.roll(context, "1d20")
    context.send.assert_called_once_with("**Rolls**: results\n**Total**: 1")
