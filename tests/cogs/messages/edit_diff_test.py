from unittest import mock

import pytest

from duckbot.cogs.messages import EditDiff


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.Message")
@pytest.mark.parametrize(
    "before_text,after_text,diff",
    [
        ("replace", "word", "[-replace-]{+word+}"),
        ("add space", "add   space", "add[- -]{+   +}space"),
        ("add word", "add middle word", "add {+middle +}word"),
        ("add", "add word", "add{+ word+}"),
        ("word", "add word", "{+add +}word"),
        ("remove word", "remove", "remove[- word-]"),
        ("remove word", "word", "[-remove -]word"),
        ("two words", "two things", "two [-words-]{+things+}"),
        ("two words", "full change", "[-two-]{+full+} [-words-]{+change+}"),
    ],
)
async def test_show_edit_diff_typical_case(before, after, before_text, after_text, diff, bot):
    before.id = after.id = 1
    before.clean_content = before_text
    after.clean_content = after_text
    clazz = EditDiff(bot)
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_called_once_with(f":eyes: {after.author.mention}.\n{diff}", delete_after=300)


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.Message")
async def test_show_edit_diff_bot_author_before(before, after, bot):
    before.author = bot.user
    clazz = EditDiff(bot)
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.Message")
async def test_show_edit_diff_bot_author_after(before, after, bot):
    after.author = bot.user
    clazz = EditDiff(bot)
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.Message")
async def test_show_edit_diff_bot_content_same(before, after, bot):
    before.content = after.content = "embeds trigger this for some reason, who knows"
    clazz = EditDiff(bot)
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_not_called()
