import discord
import os.path
import pytest
from duckbot.logging import GetLogs


@pytest.mark.asyncio
async def test_get_logs_sends_tarball_of_logs(bot, context):
    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)

    assert "file" in context.send.call_args.kwargs
    assert isinstance(context.send.call_args.kwargs["file"], discord.file.File)
    assert context.send.call_args.kwargs["file"].filename == "logs.tar.gz"


@pytest.mark.asyncio
async def test_get_logs_delete_tarball_of_logs(bot, context):
    clazz = GetLogs(bot)
    await clazz._GetLogs__logs(context)
    assert not os.path.exists(os.path.join(os.getcwd(), "logs.tar.gz"))
