import pytest
import mock
import urllib.request
from async_mock_ext import patch_async_mock
from cogs.typos import Typos

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
@mock.patch('urllib.request.urlopen')
async def test_get_wiki_corrections(bot, open):
    open.return_value = mock_read("<html></html>")
    clazz = Typos(bot)
    print(clazz.get_wiki_corrections())

def mock_read(html):
    read = mock.MagicMock()
    read.getcode.return_value = 200
    read.read.return_value = html
    return read
