import gzip
import subprocess
from unittest import mock

import discord
import pytest
from sqlalchemy.engine import make_url

from duckbot.db.pg import Pg
from tests.discord_test_ext import bind_commands

ARGS = ["--host", "postgres", "--username", "duckbot", "--dbname", "duckbot"]


@pytest.fixture
def clazz(bot, db) -> Pg:
    db.db.url = make_url("postgresql+psycopg2://duckbot:pond@postgres/duckbot")
    return bind_commands(Pg(bot, db))


@pytest.fixture
def attachment(autospec) -> discord.Attachment:
    a = autospec.of(discord.Attachment)
    a.filename = "duckbot.sql"
    a.read.return_value = b"-- dump"
    return a


def completed(returncode: int = 0, stdout: bytes = b"", stderr: bytes = b"") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


async def test_pg_without_subcommand(clazz, context):
    await clazz.pg(context)
    context.send.assert_called_once_with("`!pg dump`, or `!pg restore` with the dump attached, brother.")


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_dump_runs_pg_dump_against_the_bot_database(run, clazz, context):
    run.return_value = completed(stdout=b"-- dump")
    await clazz.dump(context)
    assert run.call_args.args[0] == ["pg_dump", "--clean", "--if-exists"] + ARGS
    assert run.call_args.kwargs["env"]["PGPASSWORD"] == "pond"


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_dump_sends_archive_to_author(run, clazz, context):
    run.return_value = completed(stdout=b"-- dump")
    await clazz.dump(context)
    archive = context.author.send.call_args.kwargs["file"]
    assert archive.filename == "duckbot.sql.gz"
    assert gzip.decompress(archive.fp.read()) == b"-- dump"
    context.send.assert_called_once_with("Sent it to your DMs, brother.")


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_dump_failed(run, clazz, context):
    run.return_value = completed(returncode=1, stderr=b"could not connect\n")
    await clazz.dump(context)
    context.author.send.assert_not_called()
    context.send.assert_called_once_with("`pg_dump` fell over, brother:\n```could not connect```")


async def test_restore_without_attachment(clazz, context):
    context.message.attachments = []
    await clazz.restore(context)
    context.send.assert_called_once_with("Attach a dump to restore, brother.")


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_restore_pipes_dump_to_psql(run, clazz, context, attachment):
    run.return_value = completed()
    context.message.attachments = [attachment]
    await clazz.restore(context)
    assert run.call_args.args[0] == ["psql", "--variable", "ON_ERROR_STOP=1"] + ARGS
    assert run.call_args.kwargs["input"] == b"-- dump"
    context.send.assert_called_once_with("Restored, brother.")


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_restore_gunzips_archive(run, clazz, context, attachment):
    run.return_value = completed()
    attachment.filename = "duckbot.sql.gz"
    attachment.read.return_value = gzip.compress(b"-- dump")
    context.message.attachments = [attachment]
    await clazz.restore(context)
    assert run.call_args.kwargs["input"] == b"-- dump"


@mock.patch("duckbot.db.pg.subprocess.run")
async def test_restore_failed(run, clazz, context, attachment):
    run.return_value = completed(returncode=1, stderr=b"syntax error\n")
    context.message.attachments = [attachment]
    await clazz.restore(context)
    context.send.assert_called_once_with("`psql` fell over, brother:\n```syntax error```")
