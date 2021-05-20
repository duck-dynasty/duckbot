import pytest

import duckbot
from duckbot.__main__ import run_duckbot

DISCORD_TOKEN = "discord-token"


@pytest.fixture(autouse=True)
def set_discord_token_env(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", DISCORD_TOKEN)


def test_run_duckbot_connection_test(bot_spy, monkeypatch):
    monkeypatch.setenv("DUCKBOT_ARGS", "connection-test")
    run_duckbot(bot_spy)
    bot_spy.load_extension.assert_any_call(duckbot.util.connection_test.__name__)
    bot_spy.run.assert_called_once_with(DISCORD_TOKEN)


def test_run_duckbot_normal_run(bot_spy):
    run_duckbot(bot_spy)
    bot_spy.run.assert_called_once_with(DISCORD_TOKEN)
