import pytest
import mock
from async_mock_ext import patch_async_mock
from duckbot.cogs.tito import Tito

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_react_to_tito_with_yugoslavia_bot_author(message, bot):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Tito(bot)
    msg = await clazz.react_to_tito_with_yugoslavia(message)
    assert msg == None
    message.add_reaction.assert_not_called()

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_react_to_tito_with_yugoslavia_message_contains_tito_text(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = "josip bro :tito:, brother"
    clazz = Tito(bot)
    msg = await clazz.react_to_tito_with_yugoslavia(message)
    assert msg == None
    assert_flags_sent(message)

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.Message')
@mock.patch('discord.ext.commands.Bot')
async def test_react_to_tito_with_yugoslavia_message_contains_tito_emoji(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = "josip bro <:tito:780954015285641276>, brother"
    clazz = Tito(bot)
    msg = await clazz.react_to_tito_with_yugoslavia(message)
    assert msg == None
    assert_flags_sent(message)

def assert_flags_sent(message):
    calls = [
        mock.call("\U0001F1E7\U0001F1E6"),
        mock.call("\U0001F1ED\U0001F1F7"),
        mock.call("\U0001F1FD\U0001F1F0"),
        mock.call("\U0001F1F2\U0001F1EA"),
        mock.call("\U0001F1F2\U0001F1F0"),
        mock.call("\U0001F1F7\U0001F1F8"),
        mock.call("\U0001F1F8\U0001F1EE"),
    ]
    message.add_reaction.assert_has_calls(calls, any_order = True)
