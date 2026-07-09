"""quarterly seasons

Revision ID: 004_quarterly_seasons
Revises: 003_playmarket
Create Date: 2026-07-09

"""

from datetime import datetime
from typing import Sequence, Union
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision: str = "004_quarterly_seasons"
down_revision: Union[str, None] = "003_playmarket"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Season.ends_at is now derived from starts_at (see models._next_quarter_start), so the column is
# redundant. Reset the currently running season's clock to roughly now, so it lands on the next
# quarter boundary (2026-10-01) instead of whatever the old ~6-month timedelta happened to leave it at.
RESTART = datetime(2026, 7, 9, tzinfo=ZoneInfo("US/Eastern"))


def _next_quarter_start(dt: datetime) -> datetime:
    month = (dt.month - 1) // 3 * 3 + 4
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return dt.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def upgrade() -> None:
    seasons = sa.table("pm_seasons", sa.column("status", sa.String), sa.column("starts_at", sa.DateTime(timezone=True)))
    op.execute(seasons.update().where(seasons.c.status == "active").values(starts_at=RESTART))
    op.drop_column("pm_seasons", "ends_at")


def downgrade() -> None:
    op.add_column("pm_seasons", sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True))
    seasons = sa.table("pm_seasons", sa.column("id", sa.BigInteger), sa.column("starts_at", sa.DateTime(timezone=True)), sa.column("ends_at", sa.DateTime(timezone=True)))
    conn = op.get_bind()
    for sid, starts_at in conn.execute(sa.select(seasons.c.id, seasons.c.starts_at)):
        conn.execute(seasons.update().where(seasons.c.id == sid).values(ends_at=_next_quarter_start(starts_at)))
    with op.batch_alter_table("pm_seasons") as batch:
        batch.alter_column("ends_at", nullable=False)
