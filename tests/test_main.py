import sys
import mock
from unittest.mock import call
from discord import Intents
from duckbot.__main__ import run_duckbot, intents
from duckbot.util import ConnectionTest


def test_intents_has_required_permissions():
    expected = Intents.none()
    expected.guilds = True
    expected.emojis = True
    expected.messages = True
    expected.reactions = True
    assert intents() == expected


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_run_duckbot_connection_test(bot, loop):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        run_duckbot(bot)
        assert_cog_added(bot, ConnectionTest)
        bot.run.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_run_duckbot_normal_run(bot, loop):
    run_duckbot(bot)
    bot.run.assert_called()


def assert_cog_added(bot, typ):
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0], typ):
            return True
    return False
