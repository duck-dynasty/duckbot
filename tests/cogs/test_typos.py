import pytest
import mock
from duckmock.urllib import patch_urlopen
from duckmock.discord import MockAsyncIterator
from cogs.typos import Typos


@pytest.mark.asyncio
async def test_get_custom_corrections():
    clazz = Typos(None, start_tasks=False)
    assert clazz._Typos__get_custom_corrections() is not None


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
async def test_get_wiki_corrections(bot):
    with patch_urlopen(content("poo->oops")):
        clazz = Typos(bot, start_tasks=False)
        corrections = clazz.get_wiki_corrections()
        assert corrections == {"poo": ["oops"]}


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
async def test_correct(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot, start_tasks=False)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.correct("poo")
        assert correction == "oops"


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
async def test_correct_case_insensitive(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot, start_tasks=False)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.correct("PoO")
        assert correction == "oops"


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Message")
async def test_correct_typos_bot_user(bot, message):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Typos(bot, start_tasks=False)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Message")
async def test_correct_typos_message_is_not_fuck(bot, message):
    bot.user = "THEBOT"
    message.author = "not the bot"
    message.content = "poopy"
    clazz = Typos(bot, start_tasks=False)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Message")
@mock.patch("discord.TextChannel")
async def test_correct_typos_no_previous_message(bot, message, channel):
    bot.user = "THEBOT"
    message.author = "not the bot"
    message.content = "fuck"
    message.channel = channel
    channel.history.return_value = MockAsyncIterator(None)
    clazz = Typos(bot, start_tasks=False)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Message")
@mock.patch("discord.TextChannel")
@mock.patch("discord.Message")
async def test_correct_typos_no_typos_in_previous(bot, message, channel, prev_message):
    bot.user = "THEBOT"
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "hello"
    message.channel = channel
    channel.history.return_value = MockAsyncIterator(prev_message)
    clazz = Typos(bot, start_tasks=False)
    clazz.corrections = {"henlo": ["hello"]}
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_called_once_with(
        f"There's no need for harsh words, {message.author.mention}."
    )


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("discord.Message")
@mock.patch("discord.TextChannel")
@mock.patch("discord.Message")
async def test_correct_typos_sends_correction(bot, message, channel, prev_message):
    bot.user = "THEBOT"
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    message.channel = channel
    prev_message.content = "henlo"
    channel.history.return_value = MockAsyncIterator(prev_message)
    clazz = Typos(bot, start_tasks=False)
    clazz.corrections = {"henlo": ["hello"]}
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_called_once_with(
        f"> hello\nThink I fixed it, {message.author.mention}!"
    )


def content(*args):
    html = "<html><pre>"
    for a in args:
        html += a
    return html + "</pre></html>"
