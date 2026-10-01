from duckbot.cogs.ai import Explain, Truth
from duckbot.cogs.ai import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot_spy):
    await extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Truth)
    assert_cog_added_of_type(bot_spy, Explain)
