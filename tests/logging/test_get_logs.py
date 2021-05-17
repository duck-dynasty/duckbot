from unittest import MagicMock, mock

import pytest

from duckbot.logging import GetLogs


@pytest.mark.asyncio
@mock.patch("tarfile.open", autospec=True)
async def test_get_logs_sends_tarball_of_logs(mock_open, bot, context):
    mock_add = MagicMock()
    mock_open.return_value.__enter__.return_value.add = mock_add

    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)

    context.send.assert_called_once()
    assert context.send.call_args.kwargs["file"].filename == "logs.tar.gz"
