from unittest import mock

import discord
import pytest

from duckbot.slash import InteractionContext


@pytest.fixture
def interaction_response(autospec) -> discord.InteractionResponse:
    """Returns a mock interaction response."""
    return autospec.of(discord.InteractionResponse)


@pytest.fixture
def interaction_followup(autospec) -> discord.Webhook:
    """Returns a mock interaction followup webhook."""
    return autospec.of(discord.Webhook)


@pytest.fixture(autouse=True)
def attach_interaction_responses(interaction, interaction_response, interaction_followup):
    interaction.response = interaction_response
    interaction.followup = interaction_followup


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
    assert clazz.view.buffer == '"one" "two"'
    assert_class_setup(clazz, bot)


def test_ctor_subcommand_options(bot, interaction, command):
    command._discordpy_include_subcommand_name = {"sub": True}
    interaction.data = {"options": [{"name": "sub", "options": [{"name": "first", "value": "one"}, {"name": "second", "value": "two"}]}]}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == 'sub "one" "two"'
    assert_class_setup(clazz, bot)


def test_ctor_subcommand_options_no_subcommand_name(bot, interaction, command):
    command._discordpy_include_subcommand_name = {"sub": False}
    interaction.data = {"options": [{"name": "sub", "options": [{"name": "first", "value": "one"}, {"name": "second", "value": "two"}]}]}
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    assert clazz.view.buffer == '"one" "two"'
    assert_class_setup(clazz, bot)


def test_interaction_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).interaction == interaction


def test_channel_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).channel == interaction.channel


def test_guild_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).guild == interaction.guild


def test_voice_client_getter(bot, interaction, command):
    voice = InteractionContext(bot=bot, interaction=interaction, command=command).voice_client
    if interaction.guild:
        assert voice is interaction.guild.voice_client
    else:
        assert voice is None


def test_message_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).message == interaction.message


def test_author_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).author == interaction.user


def test_command_getter(bot, interaction, command):
    assert InteractionContext(bot=bot, interaction=interaction, command=command).command == command


def test_command_setter(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    new_command = mock.Mock()
    clazz.command = new_command
    assert clazz.command == new_command


@pytest.mark.asyncio
async def test_send_response_message_only(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send("hi")
    interaction.response.send_message.assert_called_once_with("hi")


@pytest.mark.asyncio
@mock.patch("discord.Embed")
async def test_send_response_embed_only(embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send(embed=embed)
    interaction.response.send_message.assert_called_once_with("", embed=embed)


@pytest.mark.asyncio
@mock.patch("discord.Embed")
async def test_send_response_embeds_only(embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send(embeds=[embed])
    interaction.response.send_message.assert_called_once_with("", embeds=[embed])


@pytest.mark.asyncio
@mock.patch("discord.Embed")
async def test_send_response_message_and_embed(embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send("hi", embed=embed)
    interaction.response.send_message.assert_called_once_with("hi", embed=embed)


@pytest.mark.asyncio
@mock.patch("discord.Embed")
async def test_send_response_message_and_embeds(embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send("hi", embeds=[embed])
    interaction.response.send_message.assert_called_once_with("hi", embeds=[embed])


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_response_file_ignored(file, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    await clazz.send(file=file)
    interaction.response.send_message.assert_called_once_with("")


@pytest.mark.asyncio
async def test_send_follow_up_message_only(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        await clazz.send("hi")
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("hi")


@pytest.mark.asyncio
@mock.patch("discord.File")
async def test_send_follow_up_file_only(file, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        await clazz.send(file=file)
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("", file=file)


@pytest.mark.asyncio
@mock.patch("discord.Embed")
@mock.patch("discord.File")
async def test_send_follow_up_all_args_embed(file, embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        await clazz.send("hi", embed=embed, file=file)
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("hi", embed=embed, file=file)


@pytest.mark.asyncio
@mock.patch("discord.Embed")
@mock.patch("discord.File")
async def test_send_follow_up_all_args_embeds(file, embed, bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        await clazz.send("hi", embeds=[embed], file=file)
    interaction.response.defer.assert_called_once()
    interaction.followup.send.assert_called_once_with("hi", embeds=[embed], file=file)


@pytest.mark.asyncio
async def test_typing_starts_follow_up(bot, interaction, command):
    clazz = InteractionContext(bot=bot, interaction=interaction, command=command)
    async with clazz.typing():
        pass
    assert clazz.follow_up
    interaction.response.defer.assert_called_once()


def assert_class_setup(clazz, bot):
    assert clazz.bot == bot
    assert clazz.invoked_with is None
    assert clazz.invoked_parents == []
    assert clazz.invoked_subcommand is None
    assert clazz.command_failed is False
    assert clazz.follow_up is False
