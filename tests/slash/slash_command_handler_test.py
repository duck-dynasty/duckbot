import pytest

from duckbot.slash import SlashCommandHandler, slash_command


@pytest.mark.asyncio
async def test_handle_slash_interaction_calls_command_invoke(bot, interaction, command):
    bot.commands = [command]
    slash_command()(command)
    command.name = "command_name"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandHandler(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_handle_slash_interaction_no_matching_command(bot, interaction, command):
    bot.commands = [command]
    slash_command()(command)
    command.name = "some_other_command"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandHandler(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_not_called()


@pytest.mark.asyncio
async def test_handle_slash_interaction_only_invokes_slashes(bot, interaction, command):
    bot.commands = [command]
    command.name = "command_name"
    interaction.data = {"name": "command_name"}
    clazz = SlashCommandHandler(bot)
    await clazz.handle_slash_interaction(interaction)
    command.invoke.assert_not_called()
