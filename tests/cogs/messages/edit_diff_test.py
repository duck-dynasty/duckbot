import discord
import pytest

from duckbot.cogs.messages import EditDiff

small_edits_test_cases = [
    ("add space", "add   space", "add[- -]{+   +}space"),
    ("add word", "add small word", "add {+small +}word"),
    ("add", "add word", "add{+ word+}"),
    ("word", "add word", "{+add +}word"),
    ("remove word", "remove", "remove[- word-]"),
    ("two words", "two things", "two [-words-]{+things+}"),
]


@pytest.fixture
def before(autospec):
    msg = autospec.of(discord.Message)
    msg.author.bot = False
    return msg


@pytest.fixture
def after(autospec):
    msg = autospec.of(discord.Message)
    msg.author.bot = False
    return msg


@pytest.mark.parametrize("before_text,after_text,diff", small_edits_test_cases)
async def test_show_edit_diff_small_edit_distance(before, after, before_text, after_text, diff):
    before.clean_content = before_text
    after.clean_content = after_text
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()


@pytest.mark.parametrize(
    "before_text,after_text,diff",
    [
        ("1234567", "0000000", "[-1234567-]{+0000000+}"),
        ("replace", "word", "[-replace-]{+word+}"),
        ("remove word", "word", "[-remove -]word"),
        ("two words", "full change", "[-two-]{+full+} [-words-]{+change+}"),
        ("are you eating cake???", "I'm getting a root canal.", "[-are-]{+I'm+} [-you-]{+getting+} [-eating-]{+a+} [-cake???-]{+root canal.+}"),
        ("hi", "hi hello how are you lsoer", "hi{+ hello how are you lsoer+}"),
    ],
)
async def test_show_edit_large_edit_distance(before, after, before_text, after_text, diff):
    before.clean_content = before_text
    after.clean_content = after_text
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_called_once_with(f":eyes: {after.author.mention}.\n{diff}", delete_after=120)


@pytest.mark.parametrize("before_text,after_text,diff", small_edits_test_cases)
async def test_show_edit_test_special_user_as_before(before, after, before_text, after_text, diff):
    before.author.id = 244629273191645184
    before.clean_content = before_text
    after.clean_content = after_text
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_called_once_with(f":eyes: {after.author.mention}.\n{diff}", delete_after=120)


@pytest.mark.parametrize("before_text,after_text,diff", small_edits_test_cases)
async def test_show_edit_test_special_user_as_after(before, after, before_text, after_text, diff):
    after.author.id = 244629273191645184
    before.clean_content = before_text
    after.clean_content = after_text
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_called_once_with(f":eyes: {after.author.mention}.\n{diff}", delete_after=120)


async def test_show_edit_diff_bot_author_before(before, after):
    before.author.bot = True
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()


async def test_show_edit_diff_bot_author_after(before, after):
    after.author.bot = True
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()


async def test_show_edit_diff_bot_content_same(before, after):
    before.content = after.content = "embeds trigger this for some reason, who knows"
    clazz = EditDiff()
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()
