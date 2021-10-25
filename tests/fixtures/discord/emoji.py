import discord
import pytest


@pytest.fixture
def emoji(autospec) -> discord.Emoji:
    """Returns a mock Emoji."""
    return autospec.of(discord.Emoji)
