from unittest import mock

import pytest

from duckbot.cogs.games import CoinFlip


@pytest.mark.asyncio
@mock.patch("random.random", return_value=0.5)
@mock.patch("random.choice", return_value="some coin flip result")
async def test_coin_flip_sends_result(choice, random, bot, context):
    clazz = CoinFlip(bot)
    await clazz.coin_flip(context)
    context.send.assert_called_once_with(":coin: :coin: some coin flip result :coin: :coin:")


@pytest.mark.asyncio
@mock.patch("random.random", return_value=0.9 / 6000.0)
async def test_coin_flip_lands_on_side(random, bot, context):
    clazz = CoinFlip(bot)
    await clazz.coin_flip(context)
    context.send.assert_any_call(":coin: :coin: The Side! :coin: :coin:")
    context.send.assert_any_call("1v1 me bro: https://journals.aps.org/pre/abstract/10.1103/PhysRevE.48.2547")
