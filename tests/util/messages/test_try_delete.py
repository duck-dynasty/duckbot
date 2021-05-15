import pytest
from duckbot.util.messages import try_delete


@pytest.mark.asyncio
async def test_try_delete_only_use_case(message):
    await try_delete(message)
    message.delete.assert_called_once_with(delay=0)
