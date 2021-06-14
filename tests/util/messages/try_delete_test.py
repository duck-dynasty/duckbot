import pytest

from duckbot.util.messages import try_delete


@pytest.mark.asyncio
async def test_try_delete_deletes_message(message):
    await try_delete(message)
    message.delete.assert_called_once_with(delay=0)


@pytest.mark.asyncio
async def test_try_delete_message_is_none():
    await try_delete(None)
