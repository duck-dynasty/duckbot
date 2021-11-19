from unittest import mock

import discord
import pytest

from duckbot.cogs.games import AgeOfEmpires


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.games.aoe.get_message_reference", return_value=None)
@pytest.mark.parametrize("text", ["105", "  105  "])
async def test_expand_taunt_message_is_taunt_and_not_reply(get_message_reference, bot, message, text):
    message.content = text
    clazz = AgeOfEmpires(bot)
    await clazz.expand_taunt(message)
    message.channel.send.assert_called_once_with(f"{message.author.mention} > 105: _You can resign again._")
    message.delete.assert_called()
    get_message_reference.assert_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.games.aoe.get_message_reference")
@pytest.mark.parametrize("text", ["105", "  105  "])
async def test_expand_taunt_message_is_taunt_and_reply(get_message_reference, bot, message, text, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    message.content = text
    clazz = AgeOfEmpires(bot)
    await clazz.expand_taunt(message)
    reply.reply.assert_called_once_with(f"{message.author.mention} > 105: _You can resign again._")
    message.delete.assert_called()
    get_message_reference.assert_called()


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.games.aoe.get_message_reference")
async def test_expand_taunt_message_is_not_taunt(get_message_reference, bot, message):
    message.content = "0"
    clazz = AgeOfEmpires(bot)
    await clazz.expand_taunt(message)
    message.channel.send.assert_not_called()
    message.delete.assert_not_called()
    get_message_reference.assert_not_called()
