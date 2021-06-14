from unittest import mock

import pytest

from duckbot.health import HealthCheck


@mock.patch("asyncio.StreamWriter")
@mock.patch("asyncio.StreamReader")
def test_healthcheck_bot_user_is_none(reader, writer, bot):
    bot.user = None
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("asyncio.StreamWriter")
@mock.patch("asyncio.StreamReader")
def test_healthcheck_bot_is_not_ready(reader, writer, bot):
    bot.user = "user"
    bot.is_ready.return_value = False
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("asyncio.StreamWriter")
@mock.patch("asyncio.StreamReader")
def test_healthcheck_bot_is_closed(reader, writer, bot):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = True
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("asyncio.StreamWriter")
@mock.patch("asyncio.StreamReader")
def test_healthcheck_bot_is_slow(reader, writer, bot):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = False
    bot.latency = 1.01
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("asyncio.StreamWriter")
@mock.patch("asyncio.StreamReader")
def test_healthcheck_healthy(reader, writer, bot):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = False
    bot.latency = 0.99
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"healthy")
    writer.close.assert_called()


@pytest.mark.asyncio
@mock.patch("asyncio.start_server", return_value=None)
async def test_start_health_check_tasks(server, bot):
    clazz = HealthCheck(bot)
    await clazz.start_health_check_tasks()
