from duckbot.cogs.announce_day import AnnounceDay
from duckbot.cogs.announce_day import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


async def test_setup(bot_spy):
    await extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, AnnounceDay)
