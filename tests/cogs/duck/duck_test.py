from unittest import mock

import discord

from duckbot.cogs.duck import Duck
from duckbot.util.emojis import regional_indicator


@mock.patch("random.random", return_value=0.0001)
async def test_react_duck_random_fails(random, bot, message):
    clazz = Duck(bot)
    await clazz.react_duck(message)
    message.add_reaction.assert_not_called()


@mock.patch("random.random", return_value=0)
async def test_react_with_duckbot_not_bot_author(random, bot, message):
    clazz = Duck(bot)
    await clazz.react_with_duckbot(message)
    message.add_reaction.assert_not_called()


@mock.patch("random.random", return_value=0.01)
async def test_react_with_duckbot_random_fails(random, bot, message):
    message.author = bot.user
    clazz = Duck(bot)
    await clazz.react_with_duckbot(message)
    message.add_reaction.assert_not_called()


@mock.patch("random.random", return_value=0.009)
async def test_react_with_duckbot_random_passes(random, bot, message):
    message.author = bot.user
    clazz = Duck(bot)
    await clazz.react_with_duckbot(message)
    calls = [
        mock.call(regional_indicator("i")),
        mock.call(regional_indicator("a")),
        mock.call(regional_indicator("m")),
        mock.call(regional_indicator("d")),
        mock.call(regional_indicator("u")),
        mock.call(regional_indicator("c")),
        mock.call(regional_indicator("k")),
        mock.call(regional_indicator("b")),
        mock.call(regional_indicator("o")),
        mock.call(regional_indicator("t")),
    ]
    message.add_reaction.assert_has_calls(calls, any_order=False)


async def test_github(bot, context):
    clazz = Duck(bot)
    await clazz.github(context)
    context.send.assert_called_once_with("https://github.com/duck-dynasty/duckbot")


async def test_wiki(bot, context):
    clazz = Duck(bot)
    await clazz.wiki(context)
    context.send.assert_called_once_with("https://github.com/duck-dynasty/duckbot/wiki")


async def test_delete_command_message(bot, context):
    clazz = Duck(bot)
    await clazz.delete_command_message(context)
    context.message.delete.assert_called()


@mock.patch("duckbot.cogs.duck.duck.discord.utils.get")
async def test_post_to_duckboard_no_guild(mock_get, bot, raw_message):
    raw_message.guild = None
    clazz = Duck(bot)
    await clazz.post_to_duckboard(raw_message)
    mock_get.assert_not_called()


@mock.patch("duckbot.cogs.duck.duck.discord.utils.get", return_value=None)
async def test_post_to_duckboard_no_duckboard_channel(mock_get, bot, message, skip_if_private_channel):
    clazz = Duck(bot)
    await clazz.post_to_duckboard(message)


@mock.patch("duckbot.cogs.duck.duck.discord.utils.get")
@mock.patch("random.choice", return_value=0x3B7A57)
@mock.patch("random.random", return_value=0.000009)
async def test_react_duck_sends_to_duckboard(random, mock_choice, mock_get, bot, message, skip_if_private_channel, autospec):
    duckboard_channel = autospec.of(discord.TextChannel)
    mock_get.return_value = duckboard_channel
    message.content = "hello world"
    message.jump_url = "https://discord.com/channels/1/2/3"
    message.author.display_name = "TestUser"
    message.author.display_avatar.url = "https://example.com/avatar.png"
    message.channel.mention = "<#456>"
    clazz = Duck(bot)
    await clazz.react_duck(message)
    message.add_reaction.assert_called_once_with("\U0001f986")
    mock_get.assert_called_once_with(message.guild.text_channels, name="duckboard")
    embed = discord.Embed(description="hello world", color=0x3B7A57, url="https://discord.com/channels/1/2/3")
    embed.set_author(name="TestUser", icon_url="https://example.com/avatar.png")
    embed.add_field(name="\u200b", value="<#456>")
    duckboard_channel.send.assert_called_once_with(embed=embed)
