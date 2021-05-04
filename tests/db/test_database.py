from unittest import mock
from sqlalchemy.orm import declarative_base
from duckbot.db import Database

Base = declarative_base()


def test_ctor_creates_engine():
    clazz = Database()
    assert clazz.db is not None


def test_ctor_ensures_singleton_instance():
    c1 = Database()
    c2 = Database()
    assert c1 is c2


@mock.patch("tests.db.test_database.Base")
def test_session_creates_tables(base):
    clazz = Database()
    session = clazz.session(base)
    base.metadata.create_all.assert_called_once_with(clazz.db)
    assert session is not None
