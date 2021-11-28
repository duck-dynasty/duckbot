from unittest import mock

import discord
import pytest

from duckbot.cogs.text import MockText


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference", return_value=None)
async def test_mock_text_mocks_message_not_reply(get_message_reference, bot, context):
    clazz = MockText(bot)
    await clazz.mock_text(context, "some' message% asd")
    context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference")
async def test_mock_text_mocks_message_reply(get_message_reference, bot, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    clazz = MockText(bot)
    await clazz.mock_text(context, "some' message% asd")
    reply.reply.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference", return_value=None)
async def test_mock_text_no_message_not_reply(get_message_reference, bot, context):
    context.message.author.display_name = "bob"
    clazz = MockText(bot)
    await clazz.mock_text(context, "")
    context.send.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference")
async def test_mock_text_no_message_reply(get_message_reference, bot, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    context.message.author.display_name = "bob"
    clazz = MockText(bot)
    await clazz.mock_text(context, "")
    reply.reply.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@pytest.mark.asyncio
async def test_delete_command_message(bot, context):
    clazz = MockText(bot)
    await clazz.delete_command_message(context)
    context.message.delete.assert_called()
