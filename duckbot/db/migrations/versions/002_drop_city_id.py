"""drop city_id

Revision ID: 002_drop_city_id
Revises: 001_weather_locations
Create Date: 2026-03-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_drop_city_id"
down_revision: Union[str, None] = "001_weather_locations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("weather_locations", "city_id")


def downgrade() -> None:
    op.add_column("weather_locations", sa.Column("city_id", sa.BigInteger(), nullable=True))
