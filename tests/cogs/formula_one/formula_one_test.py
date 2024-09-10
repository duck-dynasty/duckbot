from unittest import mock

import discord
import pytest

from duckbot.cogs.formula_one import FormulaOne


@pytest.fixture
def supermax_emoji(autospec, guild):
    guild.name = "Friends Chat"
    e = autospec.of(discord.Emoji)
    e.guild = guild
    e.id = 1
    e.name = "supermax"
    e.__str__ = lambda x: "<supermax:1>"
    return e


@pytest.fixture
def setup_emojis(bot, supermax_emoji):
    bot.emojis = [supermax_emoji]


async def test_store_emojis_emojis_exist(bot, supermax_emoji, setup_emojis):
    clazz = FormulaOne(bot)
    await clazz.store_emojis()
    assert clazz.supermax == supermax_emoji


async def test_store_emojis_no_emojis_found(bot):
    bot.emojis = []
    clazz = FormulaOne(bot)
    await clazz.store_emojis()
    assert clazz.supermax is None


async def test_car_do_be_going_fast_though_not_dank_channel(bot, message, setup_emojis):
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_not_called()


@mock.patch("random.choice", return_value=["\U0001F170"])
async def test_car_do_be_going_fast_though_dank_channel(random, bot, message, setup_emojis):
    message.channel.name = "dank"
    clazz = FormulaOne(bot)
    await clazz.car_do_be_going_fast_though(message)
    message.add_reaction.assert_called_once_with("\U0001F170")
