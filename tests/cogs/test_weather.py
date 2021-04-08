import pytest
import mock
from async_mock_ext import patch_async_mock
from duckmock.urllib import patch_urlopen
from cogs.weather import Weather

URLOPEN = "urllib.request.urlopen"


@pytest.mark.asyncio
@patch_async_mock
@mock.patch('discord.ext.commands.Bot')
async def test_correct(bot):
    with patch_urlopen(content("")):
        clazz = Weather(bot, start_tasks=False)
        clazz.corrections = {"poo": ["oops"]}
        correction = clazz.get_weather("poo")
        assert correction == "oops"





def content(*args):
    html = "<html><pre>"
    for a in args:
        html += a
    return html + "</pre></html>"
