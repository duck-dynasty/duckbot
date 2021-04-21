import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.health import setup as extension_setup, HealthCheck


@pytest.mark.asyncio
async def test_setup(bot):
    extension_setup(bot)
    assert_cog_added_of_type(bot, HealthCheck)
