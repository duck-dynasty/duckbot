"""Test scaffolding: runs the cog against a real in-memory SQLite database."""

import datetime
from unittest import mock

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from duckbot.cogs.playmarket.market import PlayMarket
from duckbot.cogs.playmarket.models import (
    Base,
    LedgerEntry,
    Market,
    PlayerAccount,
    Position,
)


@compiles(BigInteger, "sqlite")
def _bigint_as_integer(type_, compiler, **kw):
    return "INTEGER"  # SQLite auto-increments INTEGER, not BIGINT


class FakeDatabase:
    """Stand-in for duckbot.db.Database backed by one in-memory SQLite database."""

    def __init__(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)  # keep rows readable after close

    def session(self, _model):
        return self._sessions()


class Clock:
    """A movable replacement for now()."""

    def __init__(self):
        self.t = datetime.datetime(2024, 1, 1, 12, 0)

    def __call__(self):
        return self.t

    def advance(self, **kwargs):
        self.t += datetime.timedelta(**kwargs)
        return self.t


@pytest.fixture
def db():
    return FakeDatabase()


@pytest.fixture
def clock():
    movable = Clock()
    with mock.patch("duckbot.cogs.playmarket.market.now", side_effect=movable):
        yield movable


@pytest.fixture
def cog(bot, db, clock):
    market = PlayMarket(bot, db)
    market.tick_loop.cancel()  # don't run the loop mid-test
    return market


def make_context(user_id, display_name=None, guild=True, manage_guild=True):
    """A minimal command context."""
    ctx = mock.Mock()
    ctx.author = mock.Mock(id=user_id, display_name=display_name or f"user{user_id}")
    ctx.author.guild_permissions.manage_guild = manage_guild
    if guild:
        ctx.guild.get_member = lambda uid: mock.Mock(id=uid, display_name=f"user{uid}")
    else:
        ctx.guild = None
    ctx.send = mock.AsyncMock()
    ctx.bot.is_owner = mock.AsyncMock(return_value=False)
    return ctx


@pytest.fixture
def alice():
    return make_context(1)


@pytest.fixture
def bob():
    return make_context(2)


@pytest.fixture
def carol():
    return make_context(3)


# --- read/assert helpers -------------------------------------------------


def account(db, user_id):
    with db.session(PlayerAccount) as session:
        return session.get(PlayerAccount, user_id)


def market_row(db, market_id):
    with db.session(Market) as session:
        return session.get(Market, market_id)


def position(db, user_id, market_id):
    with db.session(Position) as session:
        return session.get(Position, (user_id, market_id))


def ledger(db, user_id):
    with db.session(LedgerEntry) as session:
        return session.query(LedgerEntry).filter_by(user_id=user_id).all()


def reconciles(db):
    """Each player's balance equals their ledger sum."""
    with db.session(PlayerAccount) as session:
        for player in session.query(PlayerAccount).all():
            total = sum((e.delta for e in session.query(LedgerEntry).filter_by(user_id=player.id).all()), 0)
            if player.balance != total:
                return False
    return True


def set_balance(db, user_id, amount):
    with db.session(PlayerAccount) as session:
        session.get(PlayerAccount, user_id).balance = int(amount)
        session.commit()


async def open_market(cog, ctx, liquidity="med"):
    """Create a market and return its id."""
    await cog.create(ctx, "Will it happen?", "official ruling", liquidity)
    with cog.db.session(Market) as session:
        return session.query(Market).order_by(Market.id.desc()).first().id
