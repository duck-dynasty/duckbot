import asyncio
import datetime
from unittest import mock

import pytest

from duckbot.logs import loop_replacement


@pytest.mark.asyncio
@mock.patch("traceback.format_exception")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_loop_replacement_adds_error_handler_as_function(logger, get_logger, format_exc):
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
    assert func.get_task().exception() is not None
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
    assert wrapper.func.get_task().exception() is not None
    format_exc.assert_called_once()
    get_logger.assert_called_once_with(wrapper.__module__)
    logger.error.assert_called_once()
