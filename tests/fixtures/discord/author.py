import discord
import pytest


@pytest.fixture
def user(autospec) -> discord.User:
    """Returns a mock discord User, someone in a private channel (eg DM)."""
    u = autospec.of(discord.User)
    u.bot = False
    return u


@pytest.fixture
def bot_user(autospec) -> discord.User:
    """Returns a mock discord User that is a bot."""
    u = autospec.of(discord.User)
    u.bot = True
    return u


@pytest.fixture
def member(autospec) -> discord.Member:
    """Returns a mock discord Member, someone in a discord server."""
    m = autospec.of(discord.Member)
    m.bot = False
    return m


@pytest.fixture
def bot_member(autospec) -> discord.Member:
    """Returns a mock discord Member that is a bot."""
    m = autospec.of(discord.Member)
    m.bot = True
    return m
