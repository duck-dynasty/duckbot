from unittest.mock import call

import pytest

import duckbot.util.connection_test
from duckbot.__main__ import run_duckbot

DISCORD_TOKEN = "discord-token"


@pytest.fixture(autouse=True)
def set_discord_token_env(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", DISCORD_TOKEN)


async def test_run_duckbot_connection_test(bot_spy, monkeypatch):
    monkeypatch.setenv("DUCKBOT_ARGS", "connection-test")
    await run_duckbot(bot_spy)
    assert_extensions_loaded(bot_spy, [duckbot.util.connection_test.__name__])
    bot_spy.start.assert_called_once_with(DISCORD_TOKEN)


async def test_run_duckbot_normal_run(bot_spy):
    await run_duckbot(bot_spy)
    assert_extensions_loaded(bot_spy)
    bot_spy.start.assert_called_once_with(DISCORD_TOKEN)


def assert_extensions_loaded(bot_spy, additional_extensions=[]):
    extensions = [
        "duckbot.logs",
        "duckbot.health",
        "duckbot.slash",
        "duckbot.cogs.announce_day",
        "duckbot.cogs.audio",
        "duckbot.cogs.corrections",
        "duckbot.cogs.dogs",
        "duckbot.cogs.duck",
        "duckbot.cogs.formula_one",
        "duckbot.cogs.fortune",
        "duckbot.cogs.games",
        "duckbot.cogs.github",
        "duckbot.cogs.google",
        "duckbot.cogs.insights",
        "duckbot.cogs.math",
        "duckbot.cogs.messages",
        "duckbot.cogs.recipe",
        "duckbot.cogs.robot",
        "duckbot.cogs.text",
        "duckbot.cogs.tito",
        "duckbot.cogs.weather",
    ]
    bot_spy.load_extension.assert_has_calls([call(x) for x in extensions + additional_extensions], any_order=True)
