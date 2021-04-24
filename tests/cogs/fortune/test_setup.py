import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.cogs.fortune import setup as extension_setup, Fortune


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Fortune)
