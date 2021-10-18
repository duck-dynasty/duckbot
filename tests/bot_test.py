import pytest
from discord import Intents

from duckbot import DuckBot
from duckbot.bot import intents


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
    await bot.close()


@pytest.mark.asyncio
async def test_ready_for_code_coverage(bot_spy):
    await bot_spy.ready()
