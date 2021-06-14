from unittest import mock

from sqlalchemy.orm import declarative_base

from duckbot.db import Database

Base = declarative_base()


@mock.patch("duckbot.db.database.create_engine")
def test_db_creates_engine_if_not_exists(create):
    clazz = Database()
    assert clazz.db is not None


@mock.patch("duckbot.db.database.create_engine")
def test_db_creates_engine_reuses_existing(create):
    clazz = Database()
    first = clazz.db
    second = clazz.db
    assert first == second


def test_ctor_ensures_singleton_instance():
    c1 = Database()
    c2 = Database()
    assert c1 is c2


@mock.patch("tests.db.database_test.Base")
@mock.patch("duckbot.db.database.create_engine")
def test_session_creates_tables(create, base):
    clazz = Database()
    session = clazz.session(base)
    base.metadata.create_all.assert_called_once_with(clazz.db)
    assert session is not None
