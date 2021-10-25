import discord
import pytest


@pytest.fixture
def user(autospec) -> discord.User:
    """Returns a mock discord User, someone in a private channel (eg DM)."""
    return autospec.of(discord.User)


@pytest.fixture
def member(autospec) -> discord.Member:
    """Returns a mock discord Member, someone in a discord server."""
    return autospec.of(discord.Member)
