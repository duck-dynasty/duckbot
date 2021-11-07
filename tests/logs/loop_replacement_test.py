import asyncio
import datetime
from unittest import mock

import pytest

from duckbot.logs import loop_replacement


@pytest.mark.asyncio
@mock.patch("traceback.format_exception")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_loop_replacement_adds_error_handler_only_error_arg(logger, get_logger, format_exc):
    get_logger.return_value = logger
    lock = asyncio.Event()
    lock.clear()

    @loop_replacement(time=datetime.datetime.utcnow().time())
    async def func():
        raise RuntimeError("blerg")

    @func.after_loop
    async def after():
        lock.set()

    func.start()
    await lock.wait()
    format_exc.assert_called_once()
    get_logger.assert_called_once_with("duckbot")
    logger.error.assert_called_once()


@pytest.mark.asyncio
@mock.patch("traceback.format_exception")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_loop_replacement_adds_error_handler_as_class_member(logger, get_logger, format_exc):
    get_logger.return_value = logger
    lock = asyncio.Event()
    lock.clear()

    class Wrapper:
        @loop_replacement(time=datetime.datetime.utcnow().time())
        async def func(self):
            raise RuntimeError("blorg")

        @func.after_loop
        async def after(self):
            lock.set()

    wrapper = Wrapper()
    wrapper.func.start()
    await lock.wait()
    format_exc.assert_called_once()
    get_logger.assert_called_once_with(wrapper.__module__)
    logger.error.assert_called_once()


# 2021-11-04 22:48:13,114:ERROR:duckbot: on_hour_loop
# Traceback (most recent call last):
# File "/opt/venv/lib/python3.8/site-packages/discord/ext/tasks/__init__.py", line 168, in _loop
# await self.coro(*args, **kwargs)
# File "/duckbot/duckbot/cogs/announce_day/announce_day.py", line 46, in on_hour_loop
# raise RuntimeError("ded")
# RuntimeError: ded
