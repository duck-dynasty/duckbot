import pytest
import mock
from async_mock_ext import patch_async_mock
from duckmock.urllib import patch_urlopen
from cogs.typos import Typos

URLOPEN = "urllib.request.urlopen"


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_get_wiki_corrections(bot):
    with patch_urlopen(content("poo->oops")):
        clazz = Typos(bot, start_tasks=False)
        corrections = clazz.get_wiki_corrections()
        assert corrections == {"poo": ["oops"]}


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_correct(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot, start_tasks=False)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.correct("poo")
        assert correction == "oops"


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_correct_case_insensitive(bot):
    with patch_urlopen(content("")):
        clazz = Typos(bot, start_tasks=False)
        clazz.corrections = {"to0": ["too"]}
        correction = clazz.correct_sentence("toO")
        assert correction == "too"


def content(*args):
    html = "<html><pre>"
    for a in args:
        html += a
    return html + "</pre></html>"
