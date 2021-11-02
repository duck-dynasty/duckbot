import logging
import os
from unittest import mock

import pytest

from duckbot.logs import Logging

LOG_DIR = "logs"
LOG_TAR_FILE = "logs.tar.gz"


@pytest.mark.asyncio
@mock.patch("logging.handlers.RotatingFileHandler")
@mock.patch("logging.Logger")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
@mock.patch("os.makedirs")
async def test_define_logs_create_logger(make_dirs, get_logger, discord, ducklog, handler):
    get_logger.side_effect = [discord, ducklog]
    mock_handler_id = handler.return_value

    Logging.define_logs()

    make_dirs.assert_called_once_with(LOG_DIR, exist_ok=True)
    handler.assert_called_once_with(filename=os.path.join(LOG_DIR, "duck.log"), mode="a", maxBytes=256000, backupCount=10)
    get_logger.assert_any_call("discord")
    discord.setLevel.assert_called_once_with(logging.INFO)
    discord.addHandler.assert_called_once_with(mock_handler_id)
    get_logger.assert_any_call("duckbot")
    ducklog.setLevel.assert_called_once_with(logging.INFO)
    ducklog.addHandler.assert_called_once_with(mock_handler_id)


@pytest.mark.asyncio
@mock.patch("discord.File")
@mock.patch("tarfile.open")
@mock.patch("tarfile.TarFile")
async def test_logs_sends_tarball_of_logs(tar, open, file, bot, context):
    open.return_value = tar
    mock_file_id = file.return_value

    clazz = Logging(bot)
    await clazz.logs(context)

    open.assert_called_once_with(LOG_TAR_FILE, "w:gz")
    tar.add.assert_called_once_with(LOG_DIR)
    tar.close.assert_called_once()
    file.assert_called_once_with(LOG_TAR_FILE, LOG_TAR_FILE)
    context.send.assert_called_once()
    assert context.send.call_args.kwargs["file"] == mock_file_id


@pytest.mark.asyncio
@mock.patch("traceback.print_exception")
@mock.patch("traceback.format_exception")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_log_command_exceptions_log_exception(get_logger, logger, format_exc, print_exc, bot, context, command):
    exception = mock.Mock(Exception)
    get_logger.return_value = logger
    command.name = "command"
    context.command = command
    context.args = ()
    context.kwargs = {}

    clazz = Logging(bot)
    await clazz.log_command_exceptions(context, exception)

    get_logger.assert_called_once_with("duckbot")
    format_exc.assert_called_once()
    logger.error.assert_called_once()
    print_exc.assert_called_once()


@pytest.mark.asyncio
@mock.patch("traceback.print_exc")
@mock.patch("traceback.format_exc")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_log_event_exceptions_log_exception(get_logger, logger, format_exc, print_exc, bot):
    get_logger.return_value = logger

    clazz = Logging(bot)
    await clazz.log_event_exceptions("event", (), {})

    get_logger.assert_called_once_with("duckbot")
    format_exc.assert_called_once()
    logger.error.assert_called_once()
    print_exc.assert_called_once()
