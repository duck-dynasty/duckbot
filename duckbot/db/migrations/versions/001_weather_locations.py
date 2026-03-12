"""initial

Revision ID: 001_weather_locations
Revises:
Create Date: 2026-03-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_weather_locations"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weather_locations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("city_id", sa.BigInteger(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("weather_locations")
