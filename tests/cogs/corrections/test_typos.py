import pytest
import mock
from asyncio import CancelledError
from tests.duckmock.urllib import patch_urlopen
from tests.duckmock.discord import MockAsyncIterator
from duckbot.cogs.corrections import Typos


@pytest.fixture(autouse=True)
def stub_wiki_fetch():
    """Stub the call to wiki to prevent the task from actually fetching data."""
    with patch_urlopen(content("poo->poop")):
        yield


@pytest.mark.asyncio
async def test_before_refresh_corrections_waits_for_bot(bot):
    clazz = Typos(bot)
    await clazz.before_refresh_corrections()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot):
    clazz = Typos(bot)
    clazz.cog_unload()
    with pytest.raises(CancelledError):
        await clazz.refresh_corrections.get_task()
    assert not clazz.refresh_corrections.is_running()


@pytest.mark.asyncio
async def test_get_custom_corrections(bot):
    clazz = Typos(bot)
    assert clazz._Typos__get_custom_corrections() is not None


@pytest.mark.asyncio
async def test_get_wiki_corrections(bot):
    with patch_urlopen(content("poo->oops")):
        clazz = Typos(bot)
        corrections = clazz.get_wiki_corrections()
        assert corrections == {"poo": ["oops"]}


@pytest.mark.asyncio
async def test_correct(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.correct("poo")
        assert correction == "oops"


@pytest.mark.asyncio
async def test_correct_case_insensitive(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.correct("PoO")
        assert correction == "oops"


@pytest.mark.asyncio
async def test_correct_typos_bot_user(bot, message):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Typos(bot)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_correct_typos_message_is_not_fuck(bot, message):
    bot.user = "THEBOT"
    message.author = "not the bot"
    message.content = "poopy"
    clazz = Typos(bot)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_correct_typos_no_previous_message(bot, message):
    bot.user = "THEBOT"
    message.author = "not the bot"
    message.content = "fuck"
    message.channel.history.return_value = MockAsyncIterator(None)
    clazz = Typos(bot)
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
async def test_correct_typos_no_typos_in_previous(prev_message, bot, message):
    bot.user = "THEBOT"
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "hello"
    message.channel.history.return_value = MockAsyncIterator(prev_message)
    clazz = Typos(bot)
    clazz.corrections = {"henlo": ["hello"]}
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_called_once_with(f"There's no need for harsh words, {message.author.mention}.")


@pytest.mark.asyncio
@mock.patch("discord.Message")
async def test_correct_typos_sends_correction(prev_message, bot, message):
    bot.user = "THEBOT"
    message.author.id = 1
    prev_message.author = message.author
    message.content = "fuck"
    prev_message.content = "henlo"
    message.channel.history.return_value = MockAsyncIterator(prev_message)
    clazz = Typos(bot)
    clazz.corrections = {"henlo": ["hello"]}
    await clazz._Typos__correct_typos(message) is None
    message.channel.send.assert_called_once_with(f"> hello\nThink I fixed it, {message.author.mention}!")


def content(*args):
    html = "<html><pre>"
    for a in args:
        html += a
    return html + "</pre></html>"
