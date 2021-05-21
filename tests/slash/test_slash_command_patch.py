import pytest

from duckbot.slash import Interaction, SlashCommandPatch, slash_command


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
