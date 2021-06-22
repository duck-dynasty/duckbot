from unittest import mock

import pytest

from duckbot.cogs.games import CoinFlip


@pytest.mark.asyncio
@mock.patch("random.choice", return_value="some coin flip result")
async def test_coin_flip_sends_result(random, bot, context):
    clazz = CoinFlip(bot)
    await clazz.coin_flip(context)
    context.send.assert_called_once_with(":coin: :coin: some coin flip result :coin: :coin:")
