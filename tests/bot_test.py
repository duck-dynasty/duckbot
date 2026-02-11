from discord import Intents

from duckbot import DuckBot
from duckbot.bot import intents


def test_intents_has_required_permissions():
    expected = Intents(
        guilds=True,
        emojis=True,
        messages=True,
        message_content=True,
        reactions=True,
        typing=True,
        voice_states=True,
    )
    assert intents() == expected


async def test_duckbot_constructor():
    bot = DuckBot()
    assert bot.command_prefix == "!"
    assert bot.help_command is None
    assert bot.intents == intents()
    await bot.close()


async def test_setup_hook_for_code_coverage(bot_spy):
    await bot_spy.setup_hook()
