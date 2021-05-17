import pytest
from discord import Game, Intents

from duckbot.duckbot import DuckBot, intents


def test_intents_has_required_permissions():
    expected = Intents.none()
    expected.guilds = True
    expected.emojis = True
    expected.messages = True
    expected.reactions = True
    expected.voice_states = True
    assert intents() == expected


@pytest.mark.asyncio
async def test_duckbot_constructor():
    bot = DuckBot()
    assert bot.command_prefix == "!"
    assert bot.help_command is None
    assert bot.intents == intents()
    assert bot.activity in [Game("Duck Game"), Game("the Banjo"), Game("Gloomhaven"), Game("with Fire"), Game("with the Boys")]
    await bot.close()


@pytest.mark.asyncio
async def test_ready_for_code_coverage(bot_spy):
    await bot_spy.ready()
