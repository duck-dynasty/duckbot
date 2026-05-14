from unittest import mock

import d20
import pytest

from duckbot.cogs.games import Dice
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
    "expression,expected",
    [
        ("adv", "2d20kh1"),
        ("advantage", "2d20kh1"),
        ("dis", "2d20kl1"),
        ("disadvantage", "2d20kl1"),
        ("ADV", "2d20kh1"),
        ("Dis", "2d20kl1"),
        ("adv+5", "2d20kh1+5"),
        ("adv +5", "2d20kh1 +5"),
        ("disadvantage-2", "2d20kl1-2"),
        ("  adv  ", "2d20kh1  "),
        ("advanced", "advanced"),
        ("disable", "disable"),
        ("1d20", "1d20"),
        ("1d20+adv", "1d20+adv"),
        ("", ""),
    ],
)
def test_resolve_advantage(expression, expected):
    assert Dice._resolve_advantage(expression) == expected


@mock.patch("d20.Roller")
async def test_roll_adv_passes_2d20kh1_to_roller(roller, context):
    roller.return_value.roll.return_value.result = "x"
    roller.return_value.roll.return_value.total = 1
    clazz = Dice()
    await clazz.roll(context, "adv")
    rolled_expression = roller.return_value.roll.call_args[0][0]
    assert rolled_expression == "2d20kh1"


@mock.patch("d20.Roller")
async def test_roll_dis_with_modifier_passes_2d20kl1_plus_modifier(roller, context):
    roller.return_value.roll.return_value.result = "x"
    roller.return_value.roll.return_value.total = 1
    clazz = Dice()
    await clazz.roll(context, "dis+3")
    rolled_expression = roller.return_value.roll.call_args[0][0]
    assert rolled_expression == "2d20kl1+3"
