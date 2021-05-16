import os.path
import pytest
from duckbot.logging import GetLogs

# TODO: Check the log file is created
#       Check stderr
#       Check that stderr matches thing in log

# TODO: This only checks the message string.
#       Should see if file actually sends


@pytest.mark.asyncio
async def test_archive_sent(bot, context):
    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)
    context.send.assert_called_once_with("duck.logs")


@pytest.mark.asyncio
async def test_archive_removed(bot, context):
    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)
    assert not os.path.exists(os.path.join(os.getcwd(), "logs.tar.gz"))
