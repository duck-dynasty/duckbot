from unittest import mock

import discord
import pytest


@pytest.fixture
@mock.patch("discord.Emoji", autospec=True)
def emoji(e) -> discord.Emoji:
    """Returns a mock Emoji."""
    return e
