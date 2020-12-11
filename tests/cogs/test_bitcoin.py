import pytest
import mock
import discord
from duckbot.cogs.bitcoin import Bitcoin

async def async_magic():
    pass
mock.MagicMock.__await__ = lambda x: async_magic().__await__()

@pytest.mark.asyncio
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
