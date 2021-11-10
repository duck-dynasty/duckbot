import pytest

from duckbot.slash import Option, SlashCommandHandler, slash_command


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


@pytest.mark.asyncio
async def test_upsert_slash_commands_no_commands(bot, http, guild):
    bot.walk_commands.return_value = []
    bot.guilds = [guild]
    clazz = SlashCommandHandler(bot)
    await clazz.upsert_slash_commands()
    bot.http.bulk_upsert_global_commands.assert_called_once_with(bot.user.id, [])
    bot.http.bulk_upsert_guild_commands.assert_called_once_with(bot.user.id, guild.id, [])


@pytest.mark.asyncio
async def test_upsert_slash_commands_create_commands(bot, http, guild, command):
    create_slash_command(command, "command_name")
    bot.walk_commands.return_value = [command]
    bot.guilds = [guild]
    clazz = SlashCommandHandler(bot)
    await clazz.upsert_slash_commands()
    bot.http.bulk_upsert_global_commands.assert_called_once_with(bot.user.id, [command.slash_ext.to_dict()])
    bot.http.bulk_upsert_guild_commands.assert_called_once_with(bot.user.id, guild.id, [command.slash_ext.to_dict()])


@pytest.mark.asyncio
async def test_upsert_slash_commands_create_subcommand(bot, http, guild, command):
    create_slash_command(command, "command_name", name="name", root="root", options=[Option(name="opt")])
    bot.walk_commands.return_value = [command]
    bot.guilds = [guild]
    clazz = SlashCommandHandler(bot)
    await clazz.upsert_slash_commands()
    bot.http.bulk_upsert_global_commands.assert_called_once_with(bot.user.id, [command.slash_ext.to_dict()])
    bot.http.bulk_upsert_guild_commands.assert_called_once_with(bot.user.id, guild.id, [command.slash_ext.to_dict()])


@pytest.mark.asyncio
async def test_upsert_slash_commands_create_subcommand_group(bot, http, guild, command, autospec):
    command2 = autospec.of("discord.ext.commands.Command")
    create_slash_command(command, "first", name="1", root="root", options=[Option(name="1")])
    create_slash_command(command2, "second", name="2", root="root", options=[Option(name="2")])
    expected = command.slash_ext
    expected.append_options(command2.slash_ext.options)
    bot.walk_commands.return_value = [command, command2]
    bot.guilds = [guild]
    clazz = SlashCommandHandler(bot)
    await clazz.upsert_slash_commands()
    bot.http.bulk_upsert_global_commands.assert_called_once_with(bot.user.id, [expected.to_dict()])
    bot.http.bulk_upsert_guild_commands.assert_called_once_with(bot.user.id, guild.id, [expected.to_dict()])


def create_slash_command(command, command_name, **kwargs):
    command.name = command_name
    command.description = f"description for {command_name}"
    slash_command(**kwargs)(command)
