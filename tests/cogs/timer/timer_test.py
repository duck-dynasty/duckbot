import datetime
from unittest import mock

import pytest

from duckbot.cogs.timer import Timer
from tests.discord_test_ext import bind_commands

noon = datetime.datetime(2026, 7, 9, 12, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture
def clazz() -> Timer:
    return bind_commands(Timer())


@pytest.mark.parametrize("duration, seconds", [("10", 600), ("90s", 90), ("2h", 7200), ("1h30m", 5400), ("1h30s", 3630), ("30m30s", 1830), ("1h30m30s", 5430)])
@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("duckbot.cogs.timer.timer.now", return_value=noon)
async def test_timer_waits_for_duration(now, sleep, clazz, context, duration, seconds):
    await clazz.timer(context, duration=duration)
    sleep.assert_called_once_with(seconds)
    context.send.assert_called_once_with(f":timer: Timer set for {duration}. If I die before then, you're on your own.")


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("duckbot.cogs.timer.timer.now", return_value=noon)
async def test_timer_pings_when_done(now, sleep, clazz, context):
    await clazz.timer(context, duration="10")
    context.channel.send.assert_called_once_with(f":alarm_clock: {context.author.mention} your timer is up!")


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("duckbot.cogs.timer.timer.now", return_value=noon)
async def test_timer_pings_with_label(now, sleep, clazz, context):
    await clazz.timer(context, duration="10", label="pizza")
    context.channel.send.assert_called_once_with(f":alarm_clock: {context.author.mention} your pizza timer is up!")


@mock.patch("asyncio.sleep", return_value=None)
@mock.patch("duckbot.cogs.timer.timer.now", return_value=noon)
async def test_timer_escapes_mentions_in_label(now, sleep, clazz, context):
    await clazz.timer(context, duration="10", label="@everyone")
    # expected string has a zero-width space after the @
    context.channel.send.assert_called_once_with(f":alarm_clock: {context.author.mention} your @​everyone timer is up!")


@pytest.mark.parametrize("duration", ["duck", "0", "1x", "m"])
async def test_timer_invalid_duration(clazz, context, duration):
    await clazz.timer(context, duration=duration)
    context.send.assert_called_once_with("I can't count that. Try something like `10`, `90s` or `1h30m`.")


@mock.patch("duckbot.cogs.timer.timer.now", return_value=noon.replace(hour=23))
async def test_timer_ends_past_bedtime(now, clazz, context):
    await clazz.timer(context, duration="1h")
    context.send.assert_called_once_with("I'm asleep by then... screw flanders.")
