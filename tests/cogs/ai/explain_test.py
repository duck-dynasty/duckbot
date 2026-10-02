from unittest import mock

import pytest
from groq.types import Model

from duckbot.cogs.ai import Explain
from tests import list_as_async_generator


@pytest.fixture
def clazz():
    explain = Explain()
    explain._ai_client = mock.MagicMock()
    explain._ai_client.models.list.return_value.data = [Model(id="chat", created=1, object="model", owned_by="test", active=True, output_modalities=["text"], supported_features=["tools"])]
    explain._ai_client.chat.completions.create.return_value = mock.Mock(choices=[mock.Mock(message=mock.Mock(content="It means a thing."))])
    return explain


@pytest.fixture
def referenced():
    msg = mock.Mock(clean_content="orange Cheeto man strikes again")
    msg.author.display_name = "Human1"
    msg.channel.history.return_value = list_as_async_generator([])
    return msg


def chat_message(name, content):
    msg = mock.Mock(clean_content=content)
    msg.author.display_name = name
    return msg


def prompt(clazz):
    return clazz.ai_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]


def test_create_client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake_key")
    clazz = Explain()
    assert clazz.ai_client is clazz._ai_client and clazz._ai_client is not None


async def test_explain_on_what_bot_message(clazz, bot_message):
    bot_message.content = "what"
    with mock.patch("duckbot.cogs.ai.explain.get_message_reference") as get_ref:
        await clazz.explain_on_what(bot_message)
        get_ref.assert_not_called()


async def test_explain_on_what_not_a_what(clazz, message):
    message.content = "what is that"
    with mock.patch("duckbot.cogs.ai.explain.get_message_reference") as get_ref:
        await clazz.explain_on_what(message)
        get_ref.assert_not_called()


async def test_explain_on_what_not_a_reply(clazz, message):
    message.content = "what"
    with mock.patch("duckbot.cogs.ai.explain.get_message_reference", new=mock.AsyncMock(return_value=None)):
        await clazz.explain_on_what(message)
    message.reply.assert_not_called()


@pytest.mark.parametrize("content", ["what", "WUT?", " huh?? ", "wuh", "wat!?", "wha", "whut"])
async def test_explain_on_what_replies_with_explanation(clazz, message, referenced, content):
    message.content = content
    with mock.patch("duckbot.cogs.ai.explain.get_message_reference", new=mock.AsyncMock(return_value=referenced)):
        await clazz.explain_on_what(message)
    message.reply.assert_called_once_with("It means a thing.")


async def test_explain_includes_conversation_oldest_first(clazz, referenced):
    referenced.channel.history.return_value = list_as_async_generator([chat_message("Bob", "second"), chat_message("Alice", "first")])
    await clazz.explain(referenced)
    assert 'Alice: first\nBob: second\n\nMessage to explain, from Human1:\n"orange Cheeto man strikes again"' in prompt(clazz)
