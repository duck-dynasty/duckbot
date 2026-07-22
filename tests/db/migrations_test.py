from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text

import duckbot.db
from duckbot.cogs.playmarket.models import Base as PlayMarketBase
from duckbot.cogs.weather.saved_location import Base as WeatherBase


def _alembic_config(url: str) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(Path(duckbot.db.__file__).parent / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def test_migrations_produce_model_schema(tmp_path, monkeypatch):
    """Upgrading to head yields the same schema as the models; sqlite only, so postgres-specific drift can slip by."""
    monkeypatch.delenv("DATABASE_URL", raising=False)  # env.py overrides the url when set
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    cfg = _alembic_config(url)
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    with engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        diffs = compare_metadata(context, [WeatherBase.metadata, PlayMarketBase.metadata])
    engine.dispose()
    assert diffs == []


def test_quarterly_seasons_downgrade_backfills_ends_at(tmp_path, monkeypatch):
    """Downgrading past 004 restores ends_at as the quarter boundary after starts_at."""
    monkeypatch.delenv("DATABASE_URL", raising=False)  # env.py overrides the url when set
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    cfg = _alembic_config(url)
    command.upgrade(cfg, "head")

    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO pm_seasons (name, starts_at, status, starting_balance) VALUES ('Season 1', '2026-07-09 12:00:00.000000', 'active', 10000)"))
    command.downgrade(cfg, "003_playmarket")
    with engine.connect() as conn:
        ends_at = conn.execute(text("SELECT ends_at FROM pm_seasons")).scalar_one()
    engine.dispose()
    assert datetime.fromisoformat(ends_at) == datetime(2026, 10, 1)
