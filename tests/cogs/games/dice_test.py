from unittest import mock

import d20
import pytest

from duckbot.cogs.games import Dice
from duckbot.cogs.games.dice import CRIT_FAIL_FLAVOUR, CRIT_HIT_FLAVOUR
from duckbot.util.messages import MAX_MESSAGE_LENGTH


@mock.patch("d20.Roller.roll", side_effect=[d20.RollValueError("ded")])
async def test_roll_dice_error(roller, context):
    clazz = Dice()
    await clazz.roll(context, "1d-20")
    context.send.assert_called_once_with("Oh... :nauseated_face: I don't feel so good... :face_vomiting:\n```ded```", delete_after=30)


async def test_roll_dice_too_many_dice(context):
    clazz = Dice()
    await clazz.roll(context, "100001d20")
    context.send.assert_called_once_with("I can only roll up to 100000 dice.", delete_after=30)


@mock.patch("d20.Roller")
async def test_roll_result_too_long_for_message(roller, context):
    roller.return_value.roll.return_value.result = "x" * MAX_MESSAGE_LENGTH
    roller.return_value.roll.return_value.total = 100
    clazz = Dice()
    await clazz.roll(context, "1d20")
    context.send.assert_called_once_with(f"**Rolls**: {'x' * (MAX_MESSAGE_LENGTH - 50)}...\n**Total**: 100")


@mock.patch("d20.Roller")
async def test_roll_sends_result(roller, context):
    roller.return_value.roll.return_value.result = "results"
    roller.return_value.roll.return_value.total = 1
    clazz = Dice()
    await clazz.roll(context, "1d20")
    context.send.assert_called_once_with("**Rolls**: results\n**Total**: 1")


@pytest.mark.parametrize(
    "flavour, expected_message",
    [
        (CRIT_HIT_FLAVOUR, f"{CRIT_HIT_FLAVOUR}\n**Rolls**: results\n**Total**: 20"),
        (None, "**Rolls**: results\n**Total**: 20"),
    ],
)
@mock.patch("duckbot.cogs.games.dice.Dice._crit_flavour")
@mock.patch("d20.Roller")
async def test_roll_includes_crit_flavour(roller, crit_flavour, flavour, expected_message, context):
    roller.return_value.roll.return_value.result = "results"
    roller.return_value.roll.return_value.total = 20
    crit_flavour.return_value = flavour
    clazz = Dice()
    await clazz.roll(context, "1d20")
    context.send.assert_called_once_with(expected_message)


@pytest.mark.parametrize(
    "expression, randrange_val, expected",
    [
        ("1d20", 19, CRIT_HIT_FLAVOUR),
        ("1d20", 0, CRIT_FAIL_FLAVOUR),
        ("1d20", 9, None),
        ("1d20+5", 19, CRIT_HIT_FLAVOUR),
        ("2d20", 19, None),
        ("1d6", 5, None),
    ],
)
@mock.patch("random.randrange")
def test_crit_flavour(randrange, expression, randrange_val, expected):
    randrange.return_value = randrange_val
    result = d20.roll(expression)
    assert Dice._crit_flavour(result.expr) == expected
