import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.cogs.audio import setup as extension_setup, WhoCanItBeNow


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, WhoCanItBeNow)
