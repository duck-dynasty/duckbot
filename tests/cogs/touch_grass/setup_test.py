from duckbot.cogs.touch_grass import TouchGrass
from duckbot.cogs.touch_grass import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot_spy):
    await extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, TouchGrass)
