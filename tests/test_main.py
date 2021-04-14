import sys
import mock
from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.__main__ import duckbot
from duckbot.util import ConnectionTest


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_connection_test(bot, loop):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        duckbot(bot)
        assert_cog_added_of_type(bot, ConnectionTest)
        bot.run.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_normal_run(bot, loop):
    duckbot(bot)
    bot.run.assert_called()
