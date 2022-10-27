import discord.app_commands
import discord.ext.commands
import pytest


@pytest.fixture
def command(autospec) -> discord.ext.commands.Command:
    """Returns a mock discord.py command."""
    return autospec.of(discord.ext.commands.Command)


@pytest.fixture
def tree(autospec) -> discord.app_commands.CommandTree:
    """Returns a mock discord.py command tree, ie the slash commands."""
    return autospec.of(discord.app_commands.CommandTree)
