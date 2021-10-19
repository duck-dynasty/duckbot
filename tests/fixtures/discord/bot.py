from unittest import mock

import discord.ext.tasks
import discord.http
import pytest

from duckbot import DuckBot


@pytest.fixture
async def bot_spy() -> DuckBot:
    """Returns a spy DuckBot instance with a stubbed `run` method. The bot is closed afterwards."""
    b = DuckBot()
    m = mock.Mock(wraps=b)
    m.loop = b.loop
    with mock.patch.object(DuckBot, "run"):  # stub run so it does nothing
        yield m
    await b.close()


@pytest.fixture
def bot(autospec, monkeypatch) -> DuckBot:
    """Returns a mock DuckBot instance. The default event loops are replaced by mocks."""
    b = autospec.of(DuckBot)
    b.command_prefix = "!"
    b.loop = mock.Mock()
    # mock out loop, it uses `asyncio.get_event_loop()` by default
    monkeypatch.setattr(discord.ext.tasks, "Loop", mock.Mock())
    return b


@pytest.fixture
def http(autospec, bot) -> discord.http.HTTPClient:
    """Returns a mock discord.py http client. The client is also attached to `bot.http`."""
    h = autospec.of(discord.http.HTTPClient)
    bot.http = h
    return h
