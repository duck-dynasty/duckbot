from unittest import mock

import discord
import pytest

from duckbot.cogs.text import MockText
from duckbot.cogs.text.mock_text import WRAPPERS
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz() -> MockText:
    return bind_commands(MockText())


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference", return_value=None)
async def test_mock_text_mocks_message_not_reply(get_message_reference, random_choice, random_randint, clazz, context):
    await clazz.mock_text(context, text="some' message% asd")
    context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference")
async def test_mock_text_mocks_message_reply(get_message_reference, random_choice, random_randint, clazz, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    await clazz.mock_text(context, text="some' message% asd")
    reply.reply.assert_called_once_with("SoMe' MeSsAgE% aSd")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference", return_value=None)
async def test_mock_text_no_message_not_reply(get_message_reference, random_choice, random_randint, clazz, context):
    context.message.author.display_name = "bob"
    await clazz.mock_text(context, text="")
    context.send.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="")
@mock.patch("duckbot.cogs.text.mock_text.get_message_reference")
async def test_mock_text_no_message_reply(get_message_reference, random_choice, random_randint, clazz, context, autospec):
    reply = autospec.of(discord.Message)
    get_message_reference.return_value = reply
    context.message.author.display_name = "bob"
    await clazz.mock_text(context, text="")
    reply.reply.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    get_message_reference.assert_called_once_with(context.message)


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="**")
async def test_mockify_wraps_emphasis_span_with_bold(random_choice, random_randint, clazz):
    assert clazz.mockify("hi") == "**H**i"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="*")
async def test_mockify_wraps_emphasis_span_with_italic(random_choice, random_randint, clazz):
    assert clazz.mockify("hi") == "*H*i"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="`")
async def test_mockify_wraps_emphasis_span_with_code(random_choice, random_randint, clazz):
    assert clazz.mockify("hi") == "`H`i"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", side_effect=["**", "*"])
async def test_mockify_alternates_emphasis_and_plain(random_choice, random_randint, clazz):
    assert clazz.mockify("abc") == "**A**b*C*"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=4)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="**")
async def test_mockify_spans_multiple_characters(random_choice, random_randint, clazz):
    assert clazz.mockify("hello") == "**HeLl**O"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="**")
async def test_mockify_does_not_wrap_punctuation_or_whitespace(random_choice, random_randint, clazz):
    assert clazz.mockify("hi ... bye") == "**H**i ... **B**y**E**"


@mock.patch("duckbot.cogs.text.mock_text.random.randint", return_value=1)
@mock.patch("duckbot.cogs.text.mock_text.random.choice", return_value="**")
async def test_mockify_does_not_offer_previous_wrapper_as_choice(random_choice, random_randint, clazz):
    clazz.mockify("abcde")
    assert set(random_choice.call_args_list[1][0][0]) == set(WRAPPERS) - {"**"}


async def test_delete_command_message(clazz, context):
    await clazz.delete_command_message(context)
    context.message.delete.assert_called()
