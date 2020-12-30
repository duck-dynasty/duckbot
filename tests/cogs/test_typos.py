import pytest
import mock
import urllib.request
from async_mock_ext import patch_async_mock
from mock_response import MockResponse
from cogs.typos import Typos

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_get_wiki_corrections(bot):
    html = content("poo->oops")
    with mock.patch('urllib.request.urlopen', return_value=MockResponse(data=html)) as open:
        clazz = Typos(bot, start_tasks = False)
        corrections = clazz.get_wiki_corrections()
        assert corrections == { "poo": ["oops"] }

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_correct(bot):
    html = content("poo->oops")
    with mock.patch('urllib.request.urlopen', return_value=MockResponse(data=html)) as open:
        clazz = Typos(bot, start_tasks = False)
        clazz.corrections = { "poo": ["oops"] }
        correction = clazz.correct("poo")
        assert correction == "oops"

@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_correct_case_insensitive(bot):
    html = content("poo->oops")
    with mock.patch('urllib.request.urlopen', return_value=MockResponse(data=html)) as open:
        clazz = Typos(bot, start_tasks = False)
        clazz.corrections = { "poo": ["oops"] }
        correction = clazz.correct("PoO")
        assert correction == "oops"

def content(*args):
    str = "<html><pre>"
    for a in args:
        str += a
    return str + "</pre></html>"
