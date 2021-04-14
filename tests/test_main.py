import sys
import mock
from unittest.mock import call
from duckbot.__main__ import duckbot
from duckbot.util import ConnectionTest


def test_duckbot_connection_test(bot):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        duckbot(bot)
        assert_cog_added(bot, ConnectionTest)
        bot.run.assert_called()


def test_duckbot_normal_run(bot):
    duckbot(bot)
    bot.run.assert_called()


def assert_cog_added(bot, typ):
    for invocation in bot.add_cog.call_args_list:
        if isinstance(invocation[0], typ):
            return True
    return False
