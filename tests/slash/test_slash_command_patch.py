from unittest import mock

import pytest
from discord.ext.commands import Command

from duckbot.slash import Interaction, Option, SlashCommandPatch, slash_command
from duckbot.slash.option import OptionType
from duckbot.slash.route import Route8


def test_ctor_adds_parser_for_interation_create(bot):
    clazz = SlashCommandPatch(bot)
    assert bot._connection.parsers["INTERACTION_CREATE"] == clazz.parse_interaction_create


def test_parse_interaction_create(bot):
    clazz = SlashCommandPatch(bot)
    data = {"id": "123", "application_id": "456", "token": "token!", "channel_id": "10", "user": "user", "data": "d"}
    clazz.parse_interaction_create(data)
    bot.dispatch.assert_called_once_with("slash", Interaction(bot=bot, data=data))


@pytest.mark.asyncio
async def test_handle_slash_interaction_calls_command_invoke(bot, interaction, command):
    bot.commands = [command]
    slash_command()(command)
    command.name = "command_name"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandPatch(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_handle_slash_interaction_no_matching_command(bot, interaction, command):
    bot.commands = [command]
    slash_command()(command)
    command.name = "some_other_command"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandPatch(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_not_called()


@pytest.mark.asyncio
async def test_handle_slash_interaction_only_invokes_slashes(bot, interaction, command):
    bot.commands = [command]
    command.name = "command_name"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandPatch(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_not_called()


@pytest.mark.asyncio
async def test_register_commands_no_commands(bot):
    bot.walk_commands.return_value = []
    bot.http.request.return_value = []
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_called_once_with(Route8("GET", f"/applications/{bot.user.id}/commands"))


@pytest.mark.asyncio
async def test_register_commands_delete_slash(bot):
    bot.walk_commands.return_value = []
    slash = discord_slash("ice-me")
    bot.http.request.return_value = [slash]
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_any_call(Route8("GET", f"/applications/{bot.user.id}/commands"))
    bot.http.request.assert_any_call(Route8("DELETE", f"/applications/{bot.user.id}/commands/{slash['id']}"))


@pytest.mark.asyncio
async def test_register_commands_create_slash(bot):
    command = bot_slash_command("command_name")
    bot.walk_commands.return_value = [command]
    bot.http.request.return_value = []
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_any_call(Route8("GET", f"/applications/{bot.user.id}/commands"))
    bot.http.request.assert_any_call(Route8("POST", f"/applications/{bot.user.id}/commands"), json={"name": command.name, "description": command.description, "options": []})


@pytest.mark.asyncio
async def test_register_commands_create_slash_with_options(bot):
    command = bot_slash_command("command_name", options=[Option(name="opt")])
    bot.walk_commands.return_value = [command]
    bot.http.request.return_value = []
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_any_call(Route8("GET", f"/applications/{bot.user.id}/commands"))
    bot.http.request.assert_any_call(
        Route8("POST", f"/applications/{bot.user.id}/commands"),
        json={"name": command.name, "description": command.description, "options": [{"name": "opt", "description": "opt", "type": OptionType.STRING, "required": False, "options": []}]},
    )


@pytest.mark.asyncio
async def test_register_commands_create_slash_subcommand(bot):
    command = bot_slash_command("name", name="name", root="root", options=[Option(name="opt")])
    bot.walk_commands.return_value = [command]
    bot.http.request.return_value = []
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_any_call(Route8("GET", f"/applications/{bot.user.id}/commands"))
    bot.http.request.assert_any_call(
        Route8("POST", f"/applications/{bot.user.id}/commands"),
        json={
            "name": "root",
            "description": "root",
            "options": [
                {
                    "name": "name",
                    "description": "name",
                    "type": OptionType.SUB_COMMAND,
                    "required": False,
                    "options": [{"name": "opt", "description": "opt", "type": OptionType.STRING, "required": False, "options": []}],
                }
            ],
        },
    )


@pytest.mark.asyncio
async def test_register_commands_update_slash(bot):
    command = bot_slash_command("command_name", options=[Option(name="opt")])
    bot.walk_commands.return_value = [command]
    slash = discord_slash(command.name)  # ie; no options, so we expect an update
    bot.http.request.return_value = [slash]
    clazz = SlashCommandPatch(bot)
    await clazz.register_commands()
    bot.http.request.assert_any_call(Route8("GET", f"/applications/{bot.user.id}/commands"))
    bot.http.request.assert_any_call(
        Route8("POST", f"/applications/{bot.user.id}/commands"),
        json={"name": command.name, "description": command.description, "options": [{"name": "opt", "description": "opt", "type": OptionType.STRING, "required": False, "options": []}]},
    )


def discord_slash(name, options=[]):
    return {"id": hash(f"id for {name}"), "name": name, "description": f"description for {name}", "options": options}


def bot_slash_command(command_name, **kwargs):
    cmd = mock.MagicMock(spec=Command)
    cmd.name = command_name
    cmd.description = f"description for {command_name}"
    slash_command(**kwargs)(cmd)
    return cmd
