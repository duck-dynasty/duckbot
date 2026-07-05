from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

import duckbot.db
from duckbot.cogs.playmarket.models import Base as PlayMarketBase
from duckbot.cogs.weather.saved_location import Base as WeatherBase


def test_migrations_produce_model_schema(tmp_path, monkeypatch):
    """Upgrading to head yields the same schema as the models; sqlite only, so postgres-specific drift can slip by."""
    monkeypatch.delenv("DATABASE_URL", raising=False)  # env.py overrides the url when set
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(duckbot.db.__file__).parent / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    with engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        diffs = compare_metadata(context, [WeatherBase.metadata, PlayMarketBase.metadata])
    assert diffs == []
