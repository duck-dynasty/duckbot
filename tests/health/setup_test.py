from duckbot.health import HealthCheck
from duckbot.health import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot):
    await extension_setup(bot)
    assert_cog_added_of_type(bot, HealthCheck)
