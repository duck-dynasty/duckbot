import discord
import pytest

from duckbot.util.messages import get_message_reference


@pytest.fixture
def message_reference(autospec, message) -> discord.MessageReference:
    ref = autospec.of(discord.MessageReference)
    message.reference = ref
    return ref


@pytest.fixture
def reply(autospec) -> discord.Message:
    return autospec.of(discord.Message)


@pytest.mark.asyncio
async def test_get_message_reference_not_reply(message):
    message.reference = None
    reference = await get_message_reference(message)
    assert reference is None


@pytest.mark.asyncio
async def test_get_message_reference_reply_message_in_cache(message, message_reference, reply):
    message_reference.cached_message = reply
    reference = await get_message_reference(message)
    assert reference is reply


@pytest.mark.asyncio
async def test_get_message_reference_reply_message_not_in_cache(message, message_reference, reply):
    message_reference.cached_message = None
    message.channel.fetch_message.return_value = reply
    reference = await get_message_reference(message)
    assert reference is reply
    message.channel.fetch_message.assert_called_once_with(message_reference.message_id)


@pytest.mark.asyncio
async def test_get_message_reference_message_is_none():
    reference = await get_message_reference(None)
    assert reference is None
