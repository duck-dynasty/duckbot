import mock
from sqlalchemy.orm import declarative_base
from duckbot.db import Database

Base = declarative_base()


@mock.patch("discord.ext.commands.Bot")
def test_ctor_creates_engine(bot):
    clazz = Database(bot)
    assert clazz.db is not None


@mock.patch("discord.ext.commands.Bot")
@mock.patch("tests.db.test_database.Base")
def test_session_creates_tables(bot, base):
    clazz = Database(bot)
    session = clazz.session(base)
    base.metadata.create_all.assert_called_once_with(clazz.db)
    assert session is not None
