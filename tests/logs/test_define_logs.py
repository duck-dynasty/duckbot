import logging
import os
from unittest import mock

import pytest

from duckbot.logs import define_logs


@pytest.mark.asyncio
@mock.patch("logging.handlers.RotatingFileHandler")
@mock.patch("logging.Logger")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
@mock.patch("os.makedirs")
async def test_define_logs_create_logger(make_dirs, get_logger, discord, ducklog, handler):
    get_logger.side_effect = [discord, ducklog]
    mock_handler_id = handler.return_value

    define_logs()

    make_dirs.assert_called_once_with("logs", exist_ok=True)
    handler.assert_called_once_with(filename=os.path.join("logs", "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    get_logger.assert_any_call("discord")
    discord.setLevel.assert_called_once_with(logging.INFO)
    discord.addHandler.assert_called_once_with(mock_handler_id)
    get_logger.assert_any_call("duckbot")
    ducklog.setLevel.assert_called_once_with(logging.INFO)
    ducklog.addHandler.assert_called_once_with(mock_handler_id)
