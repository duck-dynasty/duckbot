import logging
import os
from unittest import mock

import pytest

from duckbot.logging.define_logs import define_logging


@pytest.mark.asyncio
@mock.patch("logging.handlers.RotatingFileHandler")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
@mock.patch("os.makedirs")
async def test_define_logs_create_logger(make_dirs, get_logger, logger, handler):
    get_logger.return_value = logger
    mock_handler_id = handler.return_value

    define_logging()

    make_dirs.assert_called_once_with("logs", exist_ok=True)
    get_logger.assert_called_once_with("discord")
    logger.setLevel.assert_called_once_with(logging.INFO)
    handler.assert_called_once_with(filename=os.path.join("logs", "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    logger.addHandler.assert_called_once_with(mock_handler_id)
