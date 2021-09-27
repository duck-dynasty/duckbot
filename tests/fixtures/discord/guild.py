import discord
import pytest


@pytest.fixture
def guild(autospec) -> discord.Guild:
    """Returns a mock Guild, ie a discord server."""
    return autospec.of("discord.Guild")
