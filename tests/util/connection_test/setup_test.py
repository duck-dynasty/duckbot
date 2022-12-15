from duckbot.util.connection_test import ConnectionTest
from duckbot.util.connection_test import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot):
    await extension_setup(bot)
    assert_cog_added_of_type(bot, ConnectionTest)
