import sys
import mock
from duckbot.__main__ import duckbot
from duckbot.util import ConnectionTest


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_dryrun(bot, loop):
    with mock.patch.object(sys, "argv", ["dry-run"]):
        duckbot(bot)
        bot.run.assert_not_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_dryrun(bot, loop):
    with mock.patch.object(sys, "argv", ["connection-test"]):
        duckbot(bot)
        bot.add_cog.assert_called
        bot.run.assert_any_call(ConnectionTest(bot))


@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.ext.tasks.Loop")
def test_duckbot_normal_run(bot, loop):
    duckbot(bot)
    bot.run.assert_called()
