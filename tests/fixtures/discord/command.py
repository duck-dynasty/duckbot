import discord.ext.commands
import pytest


@pytest.fixture
def command(autospec) -> discord.ext.commands.Command:
    """Returns a mock discord.py command."""
    return autospec.of("discord.ext.commands.Command")
