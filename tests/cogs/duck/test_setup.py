import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.cogs.duck import setup as extension_setup, Duck


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Duck)
