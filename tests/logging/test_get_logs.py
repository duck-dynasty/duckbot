import pytest
from duckbot.logging import GetLogs


@pytest.mark.asyncio
async def test_get_logs_sends_tarball_of_logs(bot, context):
    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)

    context.send.assert_called_once()
    assert context.send.call_args.kwargs["file"].filename == "logs.tar.gz"
