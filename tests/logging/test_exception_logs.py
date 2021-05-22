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
    await clazz.log_exceptions(context, exception)

    get_logger.assert_called_once_with("discord")
    format_exc.assert_called_once()
    logger.error.assert_called_once()
    print_exc.assert_called_once()
