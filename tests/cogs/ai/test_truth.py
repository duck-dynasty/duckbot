from unittest import mock

import discord
import pytest
from discord.ext import commands

from duckbot.cogs.ai import Truth


@pytest.fixture
@mock.patch("anthropic.Anthropic")
def mock_ai_client(mock_anthropic):
    instance = mock_anthropic.return_value
    instance.messages.create.return_value = mock.Mock(content=[mock.Mock(text="Fact-checked response.")])
    return instance


@pytest.fixture
def truth(bot, mock_ai_client):
    clazz = Truth(bot)
    clazz._ai_client = mock_ai_client
    return clazz


@pytest.fixture
def ctx():
    context = mock.MagicMock(spec=commands.Context)
    context.message = mock.MagicMock(spec=discord.Message)
    context.message.reference = None
    context.message.reply = mock.AsyncMock()
    context.message.channel = mock.MagicMock()
    context.message.channel.fetch_message = mock.AsyncMock()
    context.send = mock.AsyncMock()

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    context.typing.return_value = AsyncContextManagerMock()
    return context


@pytest.fixture
def message():
    return mock.Mock(content="This is a message.")


def test_create_client(bot, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake_key")
    clazz = Truth(bot)
    assert clazz._ai_client is None
    assert clazz.ai_client == clazz._ai_client
    assert clazz._ai_client is not None


def test_reuse_client(truth, mock_ai_client):
    truth._ai_client = mock_ai_client
    assert truth.ai_client == mock_ai_client


async def test_fact_check_response(truth, message):
    response = await truth.fact_check(message)
    assert response == "Fact-checked response."


async def test_fact_check_exception(truth, message):
    truth.ai_client.messages.create.side_effect = Exception("we ran out of GPUs")
    response = await truth.fact_check(message)
    assert response == "The robot uprising has been postponed due to the following error: we ran out of GPUs"


async def test_truth_no_reference(truth, ctx):
    await truth.truth.callback(truth, ctx)
    ctx.send.assert_called_once_with("⚠️ Please use this command as a reply to the message you want to fact-check. For example:\n`Reply to a message → !truth`")


async def test_truth_with_reference(truth, ctx):
    referenced_message = mock.MagicMock(spec=discord.Message)
    referenced_message.content = "Test content"
    referenced_message.author.display_name = "TestUser"
    ctx.message.reference = mock.MagicMock()
    ctx.message.reference.message_id = 123
    ctx.message.channel.fetch_message.return_value = referenced_message
    await truth.truth.callback(truth, ctx)
    ctx.message.channel.fetch_message.assert_called_once_with(123)
    ctx.message.reply.assert_called_once_with("Fact-checked response.")
