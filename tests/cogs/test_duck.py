import pytest
import mock
from async_mock_ext import patch_async_mock
from duckbot.cogs.duck import Duck

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('random.random', return_value = 0.0001)
async def test_react_duck_random_passes(message, random):
    clazz = Duck(None)
    msg = await clazz.react_duck(message)
    assert msg == None
    message.channel.add_reaction.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('random.random', return_value = 0.000009)
async def test_react_duck_random_fails(message, random):
    clazz = Duck(None)
    msg = await clazz.react_duck(message)
    assert msg == None
    message.add_reaction.assert_called_once_with("\U0001F986")
