import pytest

from duckbot.cogs.announce_day import AnnounceDay
from duckbot.cogs.announce_day import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, AnnounceDay)
