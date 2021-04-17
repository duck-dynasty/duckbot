import pytest
from duckbot.util.connection_test import ConnectionTest


@pytest.mark.asyncio
async def test_connection_success_shuts_down_bot(bot):
    clazz = ConnectionTest(bot)
    await clazz.connection_success()
    assert bot.is_closed()
