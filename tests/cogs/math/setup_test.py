import pytest

from duckbot.cogs.math import WolframAlpha
from duckbot.cogs.math import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, WolframAlpha)
