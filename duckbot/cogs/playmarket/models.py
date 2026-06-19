"""SQLAlchemy models for the play-money prediction market.

All models share one declarative Base so a single `Database.session(<any model>)` call
creates the whole `pm_*` schema and so a command can touch several tables in one transaction.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Season(Base):
    __tablename__ = "pm_seasons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)  # the season's length lives here, not in code
    status = Column(String, nullable=False, default="active")  # active|settling|archived
    starting_balance = Column(Numeric(20, 6), nullable=False, default=1000)


class PlayerAccount(Base):
    __tablename__ = "pm_users"

    id = Column(BigInteger, primary_key=True)  # discord user id
    balance = Column(Numeric(20, 6), nullable=False, default=0)
    locked = Column(Numeric(20, 6), nullable=False, default=0)  # bonds in flight
    last_topup_at = Column(DateTime(timezone=True), nullable=True)


class Market(Base):
    __tablename__ = "pm_markets"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"), nullable=False)
    creator_id = Column(BigInteger, ForeignKey("pm_users.id"), nullable=False)
    question = Column(String, nullable=False)
    rules = Column(String, nullable=False)  # the fine print that decides payout
    b = Column(Numeric(12, 4), nullable=False)  # liquidity parameter
    subsidy = Column(Numeric(20, 6), nullable=False)  # = b*ln(2), funded by the house
    q_yes = Column(Numeric(20, 6), nullable=False, default=0)
    q_no = Column(Numeric(20, 6), nullable=False, default=0)
    status = Column(String, nullable=False, default="OPEN")  # OPEN|CLOSED|PROPOSED|DISPUTED|RESOLVED|VOID
    outcome = Column(String, nullable=True)  # yes|no|void once resolved
    close_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)


class Position(Base):
    __tablename__ = "pm_positions"

    user_id = Column(BigInteger, ForeignKey("pm_users.id"), primary_key=True)
    market_id = Column(BigInteger, ForeignKey("pm_markets.id"), primary_key=True)
    yes_shares = Column(Numeric(20, 6), nullable=False, default=0)
    no_shares = Column(Numeric(20, 6), nullable=False, default=0)


class Proposal(Base):
    __tablename__ = "pm_proposals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    market_id = Column(BigInteger, ForeignKey("pm_markets.id"), nullable=False)
    proposer_id = Column(BigInteger, ForeignKey("pm_users.id"), nullable=False)
    proposed = Column(String, nullable=False)  # yes|no
    bond = Column(Numeric(20, 6), nullable=False)
    disputer_id = Column(BigInteger, ForeignKey("pm_users.id"), nullable=True)
    dispute_bond = Column(Numeric(20, 6), nullable=True)
    resolver_id = Column(BigInteger, nullable=True)  # admin who broke a dispute
    window_ends = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending|disputed|accepted|settled


class SeasonResult(Base):
    __tablename__ = "pm_season_results"  # permanent standings snapshot, written at season close

    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("pm_users.id"), primary_key=True)
    final_balance = Column(Numeric(20, 6), nullable=False)
    rank = Column(Integer, nullable=False)


class LedgerEntry(Base):
    __tablename__ = "pm_ledger"  # immutable audit log; source of truth for coin integrity

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    season_id = Column(BigInteger, ForeignKey("pm_seasons.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("pm_users.id"), nullable=False)
    market_id = Column(BigInteger, ForeignKey("pm_markets.id"), nullable=True)  # null for grants/top-ups
    delta = Column(Numeric(20, 6), nullable=False)
    reason = Column(String, nullable=False)  # season_grant|bet|sell|payout|refund|bond|bond_win|topup
    created_at = Column(DateTime(timezone=True), default=_now)
