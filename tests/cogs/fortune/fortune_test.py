from subprocess import CompletedProcess
from unittest import mock

import pytest

from duckbot.cogs.fortune import Fortune
from duckbot.util.messages import MAX_MESSAGE_LENGTH
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz() -> Fortune:
    return bind_commands(Fortune())


@mock.patch("subprocess.run")
async def test_fortune_sends_fortune(run, clazz, context):
    run.return_value = CompletedProcess([], 0, b"fortune")
    await clazz.fortune(context)
    context.send.assert_called_once_with("```fortune```")


@mock.patch("subprocess.run")
def test_get_fortune_short(run, clazz):
    run.return_value = CompletedProcess([], 0, b"fortune")
    assert clazz.get_fortune() == "```fortune```"


@mock.patch("subprocess.run")
def test_get_fortune_first_is_long(run, clazz):
    long_message = "f" * MAX_MESSAGE_LENGTH
    short_message = "f"
    run.side_effect = [CompletedProcess([], 0, long_message.encode()), CompletedProcess([], 0, short_message.encode())]
    assert clazz.get_fortune() == "```f```"
