from unittest import mock

import discord
import pytest


@pytest.fixture
@mock.patch("discord.Guild", autospec=True)
def guild(g) -> discord.Guild:
    """Returns a mock Guild, ie a discord server."""
    return g
