import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.cogs.messages import setup as extension_setup, EditDiff, Haiku


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, EditDiff)
    assert_cog_added_of_type(bot_spy, Haiku)
