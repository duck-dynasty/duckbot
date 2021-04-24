import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.cogs.corrections import setup as extension_setup, Typos, Bitcoin, Kubernetes


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Typos)
    assert_cog_added_of_type(bot_spy, Bitcoin)
    assert_cog_added_of_type(bot_spy, Kubernetes)
