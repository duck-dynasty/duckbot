from unittest import mock

import discord
import pytest


@pytest.fixture
@mock.patch("discord.User", autospec=True)
def user(u) -> discord.User:
    """Returns a mock discord User, someone in a private channel (eg DM)."""
    return u


@pytest.fixture
@mock.patch("discord.Member", autospec=True)
def member(m) -> discord.Member:
    """Returns a mock discord Member, someone in a discord server."""
    return m
