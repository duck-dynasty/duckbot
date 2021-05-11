import pytest
from unittest import mock
from discord import Intents, Game
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
@mock.patch("discord_slash.SlashCommand")
async def test_duckbot_constructor(slash):
    bot = DuckBot()
    assert bot.command_prefix == "!"
    assert bot.help_command is None
    assert bot.intents == intents()
    assert bot.activity == Game("Duck Game")
    assert bot.slash is not None
    await bot.close()


@pytest.mark.asyncio
async def test_ready_for_code_coverage(bot_spy):
    await bot_spy.ready()
