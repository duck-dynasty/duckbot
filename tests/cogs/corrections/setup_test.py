import pytest

from duckbot.cogs.corrections import Bitcoin, Kubernetes, Typos
from duckbot.cogs.corrections import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, Typos)
    assert_cog_added_of_type(bot_spy, Bitcoin)
    assert_cog_added_of_type(bot_spy, Kubernetes)
