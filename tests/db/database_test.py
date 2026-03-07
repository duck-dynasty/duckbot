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


@mock.patch("duckbot.db.database.command")
@mock.patch("duckbot.db.database.MigrationContext")
@mock.patch("duckbot.db.database.sa")
@mock.patch("duckbot.db.database.Config")
@mock.patch("duckbot.db.database.create_engine")
def test_migrate_stamps_and_upgrades_existing_db_without_alembic_version(create, config, sa, migration_context, command):
    migration_context.configure.return_value.get_current_revision.return_value = None
    sa.inspect.return_value.has_table.return_value = True
    Database().migrate()
    command.stamp.assert_called_once_with(config.return_value, "001_weather_locations")
    command.upgrade.assert_called_once_with(config.return_value, "head")


@mock.patch("duckbot.db.database.command")
@mock.patch("duckbot.db.database.MigrationContext")
@mock.patch("duckbot.db.database.sa")
@mock.patch("duckbot.db.database.Config")
@mock.patch("duckbot.db.database.create_engine")
def test_migrate_skips_stamp_for_fresh_db(create, config, sa, migration_context, command):
    migration_context.configure.return_value.get_current_revision.return_value = None
    sa.inspect.return_value.has_table.return_value = False
    Database().migrate()
    command.stamp.assert_not_called()
    command.upgrade.assert_called_once_with(config.return_value, "head")


@mock.patch("duckbot.db.database.command")
@mock.patch("duckbot.db.database.MigrationContext")
@mock.patch("duckbot.db.database.sa")
@mock.patch("duckbot.db.database.Config")
@mock.patch("duckbot.db.database.create_engine")
def test_migrate_skips_stamp_when_already_versioned(create, config, sa, migration_context, command):
    migration_context.configure.return_value.get_current_revision.return_value = "001_weather_locations"
    Database().migrate()
    command.stamp.assert_not_called()
    command.upgrade.assert_called_once_with(config.return_value, "head")
