import asyncio
from unittest import mock

import discord
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
        with mock.patch.object(discord.ext.tasks.Loop, "start"):  # stub loop start so background tasks don't actually run
            yield m
    await b.close()


@pytest.fixture
async def bot(autospec, monkeypatch) -> DuckBot:
    """Returns a mock DuckBot instance. The default event loops are replaced by mocks."""
    b = autospec.of(DuckBot)
    b.command_prefix = "!"

    # stub the bot being started already
    b.wait_until_ready = mock.Mock(spec=b.wait_until_ready)

    # set emojis to empty list; Mock has __aiter__ which causes discord.utils.get
    # to return an unawaited coroutine when iterating
    b.emojis = []

    b.loop = mock.Mock(spec=asyncio.get_event_loop())
    # mock out loop, it uses `asyncio.get_event_loop()` by default
    monkeypatch.setattr(discord.ext.tasks, "Loop", mock.Mock(spec=discord.ext.tasks.Loop))
    monkeypatch.setattr(discord.ext.tasks, "loop", mock.Mock(spec=discord.ext.tasks.loop))

    return b
