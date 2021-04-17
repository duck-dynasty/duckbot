import sys
import mock
import pytest
from unittest.mock import call
from discord import Intents
from duckbot.__main__ import duckbot, intents
from duckbot.util import ConnectionTest

DISCORD_TOKEN = "discord-token"


@pytest.fixture(autouse=True)
def set_discord_token_env(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", DISCORD_TOKEN)


def test_intents_has_required_permissions():
    expected = Intents.none()
    expected.guilds = True
    expected.emojis = True
    expected.messages = True
    expected.reactions = True
    assert intents() == expected


def test_duckbot_connection_test(bot):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        duckbot(bot)
        assert_cog_added(bot, ConnectionTest)
        bot.run.assert_called_once_with(DISCORD_TOKEN)


def test_duckbot_normal_run(bot):
    duckbot(bot)
    bot.run.assert_called_once_with(DISCORD_TOKEN)


def assert_cog_added(bot, typ):
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0], typ):
            return True
    return False
