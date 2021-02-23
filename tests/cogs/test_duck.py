import pytest
import mock
from async_mock_ext import patch_async_mock
from cogs.duck import Duck


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('random.random', return_value=0.0001)
async def test_react_duck_random_passes(message, random):
    clazz = Duck(None)
    msg = await clazz.react_duck(message)
    assert msg is None
    message.channel.add_reaction.assert_not_called()


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('random.random', return_value=0.000009)
async def test_react_duck_random_fails(message, random):
    clazz = Duck(None)
    msg = await clazz.react_duck(message)
    assert msg is None
    message.add_reaction.assert_called_once_with("\U0001F986")


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Context')
async def test_github(context):
    clazz = Duck(None)
    await clazz._Duck__github(context)
    context.send.assert_called_once_with("https://github.com/Chippers255/duckbot")
