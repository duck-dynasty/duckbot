from unittest import mock

import discord

from duckbot.cogs.text import MockText


@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.util.messages.get_message_reference", return_value=None)
async def test_mock_text_mocks_message_not_reply(get_message_reference, random_choice, context):
    clazz = MockText()
    await clazz.mock_text(context, "some' message% asd")
    context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.util.messages.get_message_reference")
async def test_mock_text_mocks_message_reply(get_message_reference, random_choice, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    clazz = MockText()
    await clazz.mock_text(context, "some' message% asd")
    reply.reply.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.util.messages.get_message_reference", return_value=None)
async def test_mock_text_no_message_not_reply(get_message_reference, random_choice, context):
    context.message.author.display_name = "bob"
    clazz = MockText()
    await clazz.mock_text(context, "")
    context.send.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.util.messages.get_message_reference")
async def test_mock_text_no_message_reply(get_message_reference, random_choice, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    context.message.author.display_name = "bob"
    clazz = MockText()
    await clazz.mock_text(context, "")
    reply.reply.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.choice", side_effect=["**", "_", ""])
async def test_mockify_wraps_words_with_bold_and_italic(random_choice):
    clazz = MockText()
    result = await clazz.mockify("one two three")
    assert result == "**OnE** _tWo_ ThReE"


@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="**")
async def test_mockify_skips_pure_punctuation_tokens(random_choice):
    clazz = MockText()
    result = await clazz.mockify("hi ... bye")
    assert result == "**Hi** ... **ByE**"


async def test_delete_command_message(context):
    clazz = MockText()
    await clazz.delete_command_message(context)
    context.message.delete.assert_called()
