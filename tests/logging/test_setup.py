import pytest

from duckbot.logging import ExceptionLogs, GetLogs
from duckbot.logging import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


@pytest.mark.asyncio
async def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, GetLogs)
    assert_cog_added_of_type(bot_spy, ExceptionLogs)
