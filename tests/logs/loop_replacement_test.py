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


# 2021-11-04 22:48:08,748:INFO:discord.client: logging in using static token
# 2021-11-04 22:48:09,085:INFO:discord.gateway: Shard ID None has sent the IDENTIFY payload.
# 2021-11-04 22:48:09,290:INFO:discord.gateway: Shard ID None has connected to Gateway: ["gateway-prd-main-jrrv",{"micros":156745,"calls":["discord-sessions-green-prd-2-93",{"micros":155817,"calls":["start_session",{"micros":145753,"calls":["api-prd-main-r7f5",{"micros":136483,"calls":["get_user",{"micros":6283},"add_authorized_ip",{"micros":10344},"get_guilds",{"micros":17738},"coros_wait",{"micros":0}]}]},"guilds_connect",{"micros":1,"calls":[]},"presence_connect",{"micros":1327,"calls":[]}]}]}] (Session ID: 5802bdd651508eb1b761255a426d6ea2).
# 2021-11-04 22:48:13,114:ERROR:duckbot: on_hour_loop
# Traceback (most recent call last):
# File "/opt/venv/lib/python3.8/site-packages/discord/ext/tasks/__init__.py", line 168, in _loop
# await self.coro(*args, **kwargs)
# File "/duckbot/duckbot/cogs/announce_day/announce_day.py", line 46, in on_hour_loop
# raise RuntimeError("ded")
# RuntimeError: ded
