import asyncio
from unittest import mock

import discord.ext.tasks
import pytest

from duckbot import DuckBot


@pytest.fixture
async def bot_spy() -> DuckBot:
    """Returns a spy DuckBot instance with a stubbed `start` method. The bot is closed afterwards."""
    b = DuckBot()
    m = mock.AsyncMock(wraps=b)
    m.loop = asyncio.get_running_loop()
    with mock.patch.object(DuckBot, "start"):  # stub start so it does nothing
        yield m
    await b.close()


@pytest.fixture
async def bot(autospec, monkeypatch) -> DuckBot:
    """Returns a mock DuckBot instance. The default event loops are replaced by mocks."""
    b = autospec.of(DuckBot)
    b.command_prefix = "!"
    b.loop = mock.Mock(spec=asyncio.get_event_loop())
    # mock out loop, it uses `asyncio.get_event_loop()` by default
    monkeypatch.setattr(discord.ext.tasks, "Loop", mock.Mock(spec=discord.ext.tasks.Loop))
    monkeypatch.setattr(discord.ext.tasks, "loop", mock.Mock(spec=discord.ext.tasks.loop))
    return b
