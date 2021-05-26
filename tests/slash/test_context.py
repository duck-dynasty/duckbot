from unittest import mock

import pytest
from discord import Embed

from duckbot.slash import InteractionContext
from duckbot.slash.route import Route8


def test_ctor_no_interaction_options(bot, interaction, command):
    interaction.data = {}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == ""
    assert_class_setup(clazz, bot)


def test_ctor_empty_interaction_options(bot, interaction, command):
    interaction.data = {"options": []}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == ""
    assert_class_setup(clazz, bot)


def test_ctor_command_options(bot, interaction, command):
    interaction.data = {"options": [{"name": "first", "value": "one"}, {"name": "second", "value": "two"}]}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == "one two"
    assert_class_setup(clazz, bot)


def test_ctor_subcommand_options(bot, interaction, command):
    command._slash_discordpy_adapt_name = {"sub": True}
    interaction.data = {"options": [{"name": "sub", "options": [{"name": "first", "value": "one"}, {"name": "second", "value": "two"}]}]}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == "sub one two"
    assert_class_setup(clazz, bot)


def test_ctor_subcommand_options_no_command_name_adapt(bot, interaction, command):
    command._slash_discordpy_adapt_name = {"sub": False}
    interaction.data = {"options": [{"name": "sub", "options": [{"name": "first", "value": "one"}, {"name": "second", "value": "two"}]}]}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == "one two"
    assert_class_setup(clazz, bot)


def test_interaction_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).interaction == interaction


def test_channel_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).channel == interaction.channel


def test_guild_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).guild == interaction.guild


def test_author_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).author == interaction.author


def test_command_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).command == command


def test_command_setter(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    new_command = mock.Mock()
    clazz.command = new_command
    assert clazz.command == new_command


@pytest.mark.asyncio
async def test_send_response(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    embed = Embed().add_field(name="name", value="value")
    await clazz.send(content="hi", embed=embed)
    json = {"type": 4, "data": {"content": "hi", "embeds": [embed.to_dict()], "tts": False}}
    route = Route8("POST", f"/interactions/{interaction.id}/{interaction.token}/callback")
    bot.http.request.assert_called_once_with(route, json=json)


@pytest.mark.asyncio
async def test_send_follow_up(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    embed = Embed().add_field(name="name", value="value")
    clazz.follow_up = True
    await clazz.send(content="hi", embed=embed)
    json = {"content": "hi", "embeds": [embed.to_dict()], "tts": False}
    route = Route8("POST", f"/webhooks/{interaction.application_id}/{interaction.token}")
    bot.http.request.assert_called_once_with(route, json=json)


@pytest.mark.asyncio
async def test_typing_starts_follow_up(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        assert clazz.follow_up
        json = {"type": 5, "data": {"content": ":thinking:"}}
        route = Route8("POST", f"/interactions/{interaction.id}/{interaction.token}/callback")
        bot.http.request.assert_called_once_with(route, json=json)


@pytest.mark.asyncio
async def test_typing_throws_error_if_called_twice(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        with pytest.raises(AssertionError):
            async with clazz.typing():
                raise Exception()


def assert_class_setup(clazz, bot):
    assert clazz.bot == bot
    assert clazz.invoked_with is None
    assert clazz.invoked_parents == []
    assert clazz.invoked_subcommand is None
    assert clazz.command_failed is False
    assert clazz._state == bot._connection
    assert clazz.follow_up is False
