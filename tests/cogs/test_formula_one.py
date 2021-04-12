import pytest
import mock
from duckbot.cogs import FormulaOne


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.TextChannel")
async def test_car_do_be_going_fast_though_not_dank_channel(message, channel):
    message.channel = channel
    channel.name = "general"
    clazz = FormulaOne(None)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.TextChannel")
@mock.patch("random.choice", return_value=["\U0001F170"])
async def test_car_do_be_going_fast_though_dank_channel(message, channel, random):
    message.channel = channel
    channel.name = "dank"
    clazz = FormulaOne(None)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_called_once_with("\U0001F170")
