import pytest
import mock
from async_mock_ext import patch_async_mock
from cogs.bitcoin import Bitcoin

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_correct_bitcoin_bot_author(message, bot):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Bitcoin(bot)
    msg = await clazz.correct_bitcoin(message)
    assert msg == None
    message.channel.send.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_correct_bitcoin_message_is_bitcoin(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = "bitcoin"
    clazz = Bitcoin(bot)
    msg = await clazz.correct_bitcoin(message)
    assert msg == None
    message.channel.send.assert_called_once_with("Magic Beans*")

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_correct_bitcoin_message_contains_bitcoin(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = " BiTcOiN   broooooooo!!!....:??"
    clazz = Bitcoin(bot)
    msg = await clazz.correct_bitcoin(message)
    assert msg == None
    message.channel.send.assert_called_once_with("Magic Beans*")
