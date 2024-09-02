from duckbot.cogs.games import (
    AgeOfEmpires,
    CoinFlip,
    Dice,
    DiscordActivity,
    OfficeHours,
)
from duckbot.cogs.games import setup as extension_setup
from duckbot.cogs.games.satisfy import Satisfy
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot_spy):
    await extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Dice)
    assert_cog_added_of_type(bot_spy, AgeOfEmpires)
    assert_cog_added_of_type(bot_spy, CoinFlip)
    assert_cog_added_of_type(bot_spy, DiscordActivity)
    assert_cog_added_of_type(bot_spy, OfficeHours)
    assert_cog_added_of_type(bot_spy, Satisfy)
