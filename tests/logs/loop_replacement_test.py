from unittest import mock

import pytest

from duckbot.logs import loop_replacement


async def func():
    """A noop function for the @loop decorator to wrap."""


@pytest.mark.asyncio
@mock.patch("traceback.print_exception")
@mock.patch("traceback.format_exception")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_loop_replacement_adds_error_handler(get_logger, logger, format_exc, print_exc):
    get_logger.return_value = logger
    loop = loop_replacement()(func)
    assert loop._error is not None
    await loop._error(RuntimeError("blerg"))
    get_logger.assert_called_once_with("duckbot")
    format_exc.assert_called_once()
    logger.error.assert_called_once()
    print_exc.assert_called_once()
