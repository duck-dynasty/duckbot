import pytest
from unittest import mock
from duckbot.cogs.formula_one import FormulaOne


@pytest.mark.asyncio
async def test_car_do_be_going_fast_though_not_dank_channel(bot, message, channel):
    message.channel = channel
    channel.name = "general"
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_not_called()


@pytest.mark.asyncio
async def test_car_do_be_going_fast_though_not_named_channel(bot, message, dm_channel):
    message.channel = dm_channel
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_not_called()


@pytest.mark.asyncio
@mock.patch("random.choice", return_value=["\U0001F170"])
async def test_car_do_be_going_fast_though_dank_channel(random, bot, message, channel):
    message.channel = channel
    channel.name = "dank"
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_called_once_with("\U0001F170")
