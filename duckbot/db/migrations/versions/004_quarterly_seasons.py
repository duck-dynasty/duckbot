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


def upgrade() -> None:
    seasons = sa.table("pm_seasons", sa.column("status", sa.String), sa.column("starts_at", sa.DateTime(timezone=True)))
    op.execute(seasons.update().where(seasons.c.status == "active").values(starts_at=RESTART))
    op.drop_column("pm_seasons", "ends_at")


def downgrade() -> None:
    op.add_column("pm_seasons", sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True))
