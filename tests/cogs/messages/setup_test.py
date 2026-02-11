from duckbot.cogs.messages import EditDiff, Haiku, Typing
from duckbot.cogs.messages import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot_spy):
    await extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, EditDiff)
    assert_cog_added_of_type(bot_spy, Haiku)
    assert_cog_added_of_type(bot_spy, Typing)
