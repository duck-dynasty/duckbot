import sys
import mock
import pytest
from tests.discord_test_ext import assert_cog_added_of_type
from discord import Intents
from duckbot.__main__ import run_duckbot, intents
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
    expected.voice_states = True
    assert intents() == expected


def test_run_duckbot_connection_test(bot_spy):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        run_duckbot(bot_spy)
        assert_cog_added_of_type(bot_spy, ConnectionTest)
        bot_spy.run.assert_called_once_with(DISCORD_TOKEN)


def test_run_duckbot_normal_run(bot_spy):
    run_duckbot(bot_spy)
    bot_spy.run.assert_called_once_with(DISCORD_TOKEN)
