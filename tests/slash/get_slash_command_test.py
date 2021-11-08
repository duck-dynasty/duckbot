import discord.ext.commands

from duckbot.slash import slash_command
from duckbot.slash.slash_command_decorator import get_slash_command


async def func():
    """A nothing function for @command to wrap."""


def test_get_slash_command_missing_slash_ext(command):
    assert get_slash_command(command) is None


def test_get_slash_command_slash_ext_is_empty(command):
    command.slash_ext = None
    assert get_slash_command(command) is None


def test_get_slash_command_slash_command():
    cmd = discord.ext.commands.command()(func)
    slash_command(root="root", name="name")(cmd)
    assert get_slash_command(cmd) is cmd.slash_ext
