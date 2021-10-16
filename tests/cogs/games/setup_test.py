import pytest

from duckbot.cogs.games import (
    AgeOfEmpires,
    CoinFlip,
    Dice,
    DiscordActivity,
    OfficeHours,
)
from duckbot.cogs.games import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Dice)
    assert_cog_added_of_type(bot_spy, AgeOfEmpires)
    assert_cog_added_of_type(bot_spy, CoinFlip)
    assert_cog_added_of_type(bot_spy, DiscordActivity)
    assert_cog_added_of_type(bot_spy, OfficeHours)
