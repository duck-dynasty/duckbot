from typing import Union

import discord.ext.commands
import pytest
from pytest_lazyfixture import lazy_fixture

import duckbot.slash


@pytest.fixture
def command_context(autospec, message) -> discord.ext.commands.Context:
    """Returns a context with nested properties set, for each channel type a command can be sent to."""
    c = autospec.of(discord.ext.commands.Context)
    c.message = message
    c.channel = message.channel
    c.author = message.author
    return c


@pytest.fixture
def interaction_context(autospec, interaction, command) -> duckbot.slash.InteractionContext:
    """Returns an interaction context with nested properties set, for each channel type a slash command can be sent to."""
    c = autospec.of(duckbot.slash.InteractionContext)
    c.interaction = interaction
    c.command = command
    c.message = interaction.message
    c.channel = interaction.channel
    c.author = interaction.user
    return c


@pytest.fixture(
    params=[
        lazy_fixture(command_context.__name__),
        lazy_fixture(interaction_context.__name__),
    ]
)
def context(request) -> Union[discord.ext.commands.Context, duckbot.slash.InteractionContext]:
    """Returns a set of discord.py command contexts and slash command contexts."""
    return request.param
