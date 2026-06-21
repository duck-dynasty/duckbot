from unittest import mock

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
@mock.patch("sqlalchemy.orm.session.Session")
def session(s):
    """Returns a mock ORM session."""
    return s


@pytest.fixture
@mock.patch("duckbot.db.Database")
def db(d, session):
    """Returns a database with a stubbed session value."""
    d.session.return_value.__enter__.return_value = session
    return d


@compiles(BigInteger, "sqlite")
def _bigint_as_integer(type_, compiler, **kw):
    return "INTEGER"  # SQLite auto-increments INTEGER, not BIGINT


class InMemoryDatabase:
    """A real duckbot.db.Database stand-in backed by one in-memory SQLite database."""

    def __init__(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)  # keep rows readable after close

    def session(self, model):
        model.metadata.create_all(self.engine)  # mirror Database.session: create tables on first use
        return self._sessions()


@pytest.fixture
def in_memory_db():
    """Returns a real database backed by in-memory SQLite, for cogs whose logic is worth testing against real rows."""
    return InMemoryDatabase()
