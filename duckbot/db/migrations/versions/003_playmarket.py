"""playmarket

Revision ID: 003_playmarket
Revises: 002_drop_city_id
Create Date: 2026-06-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_playmarket"
down_revision: Union[str, None] = "002_drop_city_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pm_seasons",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("starting_balance", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "pm_users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("balance", sa.BigInteger(), nullable=False),
        sa.Column("last_topup_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "pm_markets",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("season_id", sa.BigInteger(), sa.ForeignKey("pm_seasons.id"), nullable=False),
        sa.Column("creator_id", sa.BigInteger(), sa.ForeignKey("pm_users.id"), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("b", sa.BigInteger(), nullable=False),
        sa.Column("subsidy", sa.BigInteger(), nullable=False),
        sa.Column("q_yes", sa.Numeric(20, 6), nullable=False),
        sa.Column("q_no", sa.Numeric(20, 6), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("outcome", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "pm_positions",
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("pm_users.id"), primary_key=True),
        sa.Column("market_id", sa.BigInteger(), sa.ForeignKey("pm_markets.id"), primary_key=True),
        sa.Column("yes_shares", sa.Numeric(20, 6), nullable=False),
        sa.Column("no_shares", sa.Numeric(20, 6), nullable=False),
    )
    op.create_table(
        "pm_season_results",
        sa.Column("season_id", sa.BigInteger(), sa.ForeignKey("pm_seasons.id"), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("pm_users.id"), primary_key=True),
        sa.Column("final_balance", sa.BigInteger(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
    )
    op.create_table(
        "pm_ledger",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("season_id", sa.BigInteger(), sa.ForeignKey("pm_seasons.id"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("pm_users.id"), nullable=False),
        sa.Column("market_id", sa.BigInteger(), sa.ForeignKey("pm_markets.id"), nullable=True),
        sa.Column("delta", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("pm_ledger")
    op.drop_table("pm_season_results")
    op.drop_table("pm_positions")
    op.drop_table("pm_markets")
    op.drop_table("pm_users")
    op.drop_table("pm_seasons")
