import pytest
from unittest import mock
from duckbot.health import HealthCheck


@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.StreamReader")
@mock.patch("asyncio.StreamWriter")
def test_healthcheck_bot_user_is_none(bot, reader, writer):
    bot.user = None
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.StreamReader")
@mock.patch("asyncio.StreamWriter")
def test_healthcheck_bot_is_not_ready(bot, reader, writer):
    bot.user = "user"
    bot.is_ready.return_value = False
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.StreamReader")
@mock.patch("asyncio.StreamWriter")
def test_healthcheck_bot_is_closed(bot, reader, writer):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = True
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.StreamReader")
@mock.patch("asyncio.StreamWriter")
def test_healthcheck_bot_is_slow(bot, reader, writer):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = False
    bot.latency = 1.01
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"unhealthy")
    writer.close.assert_called()


@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.StreamReader")
@mock.patch("asyncio.StreamWriter")
def test_healthcheck_healthy(bot, reader, writer):
    bot.user = "user"
    bot.is_ready.return_value = True
    bot.is_closed.return_value = False
    bot.latency = 0.99
    clazz = HealthCheck(bot)
    clazz.healthcheck(reader, writer)
    writer.write.assert_called_once_with(b"healthy")
    writer.close.assert_called()


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.start_server", return_value=None)
async def test_start_health_check_tasks(bot, server):
    clazz = HealthCheck(bot)
    await clazz.start_health_check_tasks()
