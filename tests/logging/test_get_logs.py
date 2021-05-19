from unittest import mock

import pytest

from duckbot.logging import GetLogs


@pytest.mark.asyncio
@mock.patch("discord.File")
@mock.patch("tarfile.open")
async def test_get_logs_sends_tarball_of_logs(tar, discord_file, bot, context):
    tar.add = mock.MagicMock()
    mock_file_id = discord_file.return_value

    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)

    context.send.assert_called_once()
    assert context.send.call_args.kwargs["file"] == mock_file_id
