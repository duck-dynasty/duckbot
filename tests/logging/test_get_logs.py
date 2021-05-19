from unittest import mock

import pytest

from duckbot.logging import GetLogs


@pytest.mark.asyncio
@mock.patch("discord.File", audospec=True)
@mock.patch("tarfile.open", autospec=True)
async def test_get_logs_sends_tarball_of_logs(mock_open, mock_dis_file, bot, context):
    mock_open.add = mock.MagicMock()
    mock_file_id = mock_dis_file.return_value

    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)

    context.send.assert_called_once()
    assert context.send.call_args.kwargs["file"] == mock_file_id
