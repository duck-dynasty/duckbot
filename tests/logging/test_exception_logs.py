from unittest import mock

import pytest
from discord.ext import commands

from duckbot.logging import ExceptionLogs


@pytest.mark.asyncio
@mock.patch("traceback.print_exception")
@mock.patch("traceback.format_exception")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_exception_logs_log_exception(get_logger, logger, format_exc, print_exc, bot, context):
    exception = mock.Mock(Exception)
    cog = mock.Mock(commands.Cog)
    get_logger.return_value = logger
    context.command = ""
    context.cog = cog
    context.cog._get_overridden_method.return_value = None

    clazz = ExceptionLogs(bot)
    await clazz._ExceptionLogs__on_command_error(context, exception)

    get_logger.assert_called_once_with("discord")
    format_exc.assert_called_once()
    logger.error.assert_called_once()
    print_exc.assert_called_once()


@pytest.mark.asyncio
@mock.patch("traceback.print_exception")
@mock.patch("traceback.format_exception")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_exception_logs_has_attribute(get_logger, logger, format_exc, print_exc, bot, context):
    exception = mock.Mock(Exception)
    get_logger.return_value = logger
    context.command = mock.Mock(commands.Command)
    context.command.on_error = True

    clazz = ExceptionLogs(bot)
    await clazz._ExceptionLogs__on_command_error(context, exception)

    get_logger.assert_not_called()
    format_exc.assert_not_called()
    logger.error.assert_not_called()
    print_exc.assert_not_called()


@pytest.mark.asyncio
@mock.patch("traceback.print_exception")
@mock.patch("traceback.format_exception")
@mock.patch("logging.Logger")
@mock.patch("logging.getLogger")
async def test_exception_logs_has_override(get_logger, logger, format_exc, print_exc, bot, context):
    exception = mock.Mock(Exception)
    get_logger.return_value = logger
    context.cog.return_value = mock.Mock(commands.Cog)
    cog = context.cog.return_value
    cog._get_overridden_method.return_value = True
    context.command = ""

    clazz = ExceptionLogs(bot)
    await clazz._ExceptionLogs__on_command_error(context, exception)

    get_logger.assert_not_called()
    format_exc.assert_not_called()
    logger.error.assert_not_called()
    print_exc.assert_not_called()
