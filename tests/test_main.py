import sys
import mock
from unittest.mock import call
from duckbot.__main__ import duckbot
from duckbot.util import ConnectionTest


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_connection_test(bot, loop):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        duckbot(bot)
        assert_cog_added(bot, ConnectionTest)
        bot.run.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_normal_run(bot, loop):
    duckbot(bot)
    bot.run.assert_called()


def assert_cog_added(bot, typ):
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0], typ):
            return True
    return False
