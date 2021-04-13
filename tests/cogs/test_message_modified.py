import pytest
import mock
from duckbot.cogs import MessageModified


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_show_edit_diff(before, after, bot):
    before.id = after.id = 1
    before.content = "abc"
    after.content = "abd"
    clazz = MessageModified(bot)
    await clazz.show_edit_diff(before, after)
    after.channel.send.assert_called_once_with(f":eyes: {after.author.mention}.\nab[-c-]{{+d+}}\n")
