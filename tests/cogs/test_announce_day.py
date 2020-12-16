import pytest
import mock
from async_mock_ext import patch_async_mock
from duckbot.cogs.announce_day import AnnounceDay

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_do_announcement_7am_eastern(bot):
    clazz = AnnounceDay(bot)
    await clazz.do_announcement()
