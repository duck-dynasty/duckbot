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
