import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session


class Database:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self._db = None

    def migrate(self) -> None:
        cfg = Config("alembic.ini")
        # autostamp existing state that predates alembic; weather_locations exists but no version set
        with self.db.connect() as conn:
            ctx = MigrationContext.configure(conn)
            if ctx.get_current_revision() is None and sa.inspect(conn).has_table("weather_locations"):
                command.stamp(cfg, "001_weather_locations")
        command.upgrade(cfg, "head")

    def session(self, item_type) -> Session:
        """Returns a database session. Ensures the table described by the `item_type` is created before returning."""
        item_type.metadata.create_all(self.db)
        session = sessionmaker(self.db)
        return session()

    @property
    def db(self):
        if self._db is None:
            self._db = create_engine("postgresql+psycopg2://duckbot:pond@postgres/duckbot", pool_pre_ping=True)
        return self._db
