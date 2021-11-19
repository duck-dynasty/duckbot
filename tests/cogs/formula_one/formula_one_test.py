from unittest import mock

import pytest

from duckbot.cogs.formula_one import FormulaOne


@pytest.mark.asyncio
async def test_car_do_be_going_fast_though_not_dank_channel(bot, message):
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_not_called()


@pytest.mark.asyncio
@mock.patch("random.choice", return_value=["\U0001F170"])
async def test_car_do_be_going_fast_though_dank_channel(random, bot, message):
    message.channel.name = "dank"
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_called_once_with("\U0001F170")
