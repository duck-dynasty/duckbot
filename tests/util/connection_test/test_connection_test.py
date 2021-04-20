import pytest
from duckbot.util.connection_test import ConnectionTest


@pytest.mark.asyncio
async def test_connection_success_shuts_down_bot(bot_spy):
    clazz = ConnectionTest(bot_spy)
    await clazz.connection_success()
    bot_spy.close.assert_called()
    assert bot_spy.is_closed()
