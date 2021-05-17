import pytest

from duckbot.cogs.insights import Insights
from duckbot.cogs.insights import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot):
    extension_setup(bot)
    assert_cog_added_of_type(bot, Insights)
