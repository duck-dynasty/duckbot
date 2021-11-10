import logging
from unittest import mock

import pytest

from duckbot.logs import Logging

LOG_DIR = "logs"
LOG_TAR_FILE = "logs.tar.gz"


@pytest.mark.asyncio
@mock.patch("logging.StreamHandler")
@mock.patch("logging.handlers.RotatingFileHandler")
@mock.patch("logging.basicConfig")
@mock.patch("os.makedirs")
async def test_define_logs_create_logger(make_dirs, log_config, filehandler, streamhandler):
    Logging.define_logs()
    make_dirs.assert_called_once_with(LOG_DIR, exist_ok=True)
    log_config.assert_called_once_with(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s", handlers=[filehandler.return_value, streamhandler.return_value])


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
@mock.patch("traceback.format_exception")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_log_command_exceptions_outside_of_cog(logger, get_logger, format_exc, bot, context, command):
    exception = mock.Mock(Exception)
    get_logger.return_value = logger
    command.name = "command"
    context.command = command
    context.args = ()
    context.kwargs = {}
    context.cog = None
    context.bot = bot

    clazz = Logging(bot)
    await clazz.log_command_exceptions(context, exception)

    format_exc.assert_called_once()
    get_logger.assert_called_once_with(bot.__module__)
    logger.error.assert_called_once()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Cog")
@mock.patch("traceback.format_exception")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_log_command_exceptions_in_cog(logger, get_logger, format_exc, cog, bot, context, command):
    exception = mock.Mock(Exception)
    get_logger.return_value = logger
    command.name = "command"
    context.command = command
    context.args = ()
    context.kwargs = {}
    context.cog = cog

    clazz = Logging(bot)
    await clazz.log_command_exceptions(context, exception)

    format_exc.assert_called_once()
    get_logger.assert_called_once_with(cog.__module__)
    logger.error.assert_called_once()


@pytest.mark.asyncio
@mock.patch("traceback.format_exc")
@mock.patch("logging.getLogger")
@mock.patch("logging.Logger")
async def test_log_event_exceptions_log_exception(logger, get_logger, format_exc, bot):
    get_logger.return_value = logger
    clazz = Logging(bot)
    await clazz.log_event_exceptions("event", (), {})

    format_exc.assert_called_once()
    get_logger.assert_called_once_with("duckbot")
    logger.error.assert_called_once()
