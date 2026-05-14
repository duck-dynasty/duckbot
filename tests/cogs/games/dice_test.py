from unittest import mock

import d20

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


@mock.patch("random.randrange", return_value=19)  # randrange(20) + 1 == 20
async def test_roll_natural_20_shows_crit_hit(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "1d20")
    sent = context.send.call_args[0][0]
    assert ":dart: **Critical hit!**" in sent


@mock.patch("random.randrange", return_value=0)  # randrange(20) + 1 == 1
async def test_roll_natural_1_shows_crit_fail(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "1d20")
    sent = context.send.call_args[0][0]
    assert ":skull: **Critical fail!**" in sent


@mock.patch("random.randrange", return_value=9)  # 10
async def test_roll_middle_value_has_no_flavour(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "1d20")
    sent = context.send.call_args[0][0]
    assert "Critical" not in sent


@mock.patch("random.randrange", return_value=19)
async def test_roll_natural_20_with_modifier_still_crits(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "1d20+5")
    sent = context.send.call_args[0][0]
    assert ":dart: **Critical hit!**" in sent


@mock.patch("random.randrange", return_value=19)
async def test_roll_2d20_does_not_crit_even_with_20(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "2d20")
    sent = context.send.call_args[0][0]
    assert "Critical" not in sent


@mock.patch("random.randrange", return_value=19)
async def test_roll_d6_does_not_crit(randrange, context):
    clazz = Dice()
    await clazz.roll(context, "1d6")
    sent = context.send.call_args[0][0]
    assert "Critical" not in sent
