"""Run the bot against a local SQLite file, for manual testing without the docker-compose Postgres."""

import asyncio
import datetime
import os
import pathlib

from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles


@compiles(BigInteger, "sqlite")
def _bigint_as_integer(type_, compiler, **kw):
    return "INTEGER"  # SQLite auto-increments INTEGER, not BIGINT


def _load_env():
    """Read DISCORD_TOKEN and friends from the .env files; real env vars win."""
    for env in (pathlib.Path(".env"), pathlib.Path("duckbot/.env")):
        if env.exists():
            for line in env.read_text().splitlines():
                key, _, value = line.partition("=")
                if key.strip() and not key.strip().startswith("#"):
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    _load_env()

    import duckbot.db.database as database
    import duckbot.util.datetime
    from duckbot import DuckBot
    from duckbot.__main__ import run_duckbot

    engine = create_engine("sqlite:///duckbot-local.db")
    database.create_engine = lambda *args, **kwargs: engine  # Database.__init__ re-runs on every call, so patch the factory, not the instance
    duckbot.util.datetime.now = datetime.datetime.now  # SQLite strips tzinfo on read; keep both sides of comparisons naive

    asyncio.run(run_duckbot(DuckBot()))
