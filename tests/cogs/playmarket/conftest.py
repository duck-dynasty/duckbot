"""Test scaffolding for the play-money market.

Unlike the other DB-backed cogs (which assert on a mocked session), money logic is only
worth testing behaviourally: did the balance, the position and the ledger all end up right?
So these tests run the cog against a real in-memory SQLite database and assert on real state.
"""

import datetime
from decimal import Decimal
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
    # SQLite only auto-increments INTEGER PRIMARY KEY; production Postgres uses BIGSERIAL.
    return "INTEGER"


class FakeDatabase:
    """Stand-in for duckbot.db.Database backed by one shared in-memory SQLite database."""

    def __init__(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        # SQLite drops timezones and there are no relationships, so keep attributes readable after close.
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def session(self, _model):
        return self._sessions()


class Clock:
    """A movable replacement for `now()`; naive UTC because SQLite has no timezone type."""

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
    # SQLite has no timezone type, so keep the whole test clock naive — including the
    # absolute-date parser, which would otherwise return a tz-aware time prod Postgres keeps.
    with mock.patch("duckbot.cogs.playmarket.market.now", side_effect=movable), mock.patch("duckbot.cogs.playmarket.market.timezone", return_value=None):
        yield movable


@pytest.fixture
def cog(bot, db, clock):
    market = PlayMarket(bot, db)
    market.tick_loop.cancel()  # never let the background loop run mid-test
    return market


def make_context(user_id, display_name=None, guild=True, manage_guild=True):
    """A minimal command context: real enough to drive a command and assert on its reply."""
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
    """The core integrity invariant: each player's balance + locked equals their ledger sum."""
    with db.session(PlayerAccount) as session:
        for player in session.query(PlayerAccount).all():
            total = sum((e.delta for e in session.query(LedgerEntry).filter_by(user_id=player.id).all()), Decimal(0))
            if player.balance + player.locked != total:
                return False
    return True


def set_balance(db, user_id, amount):
    with db.session(PlayerAccount) as session:
        session.get(PlayerAccount, user_id).balance = int(amount)
        session.commit()


async def open_market(cog, ctx, closes="in 1 day", liquidity="med"):
    """Create a market through the real command path and return its id."""
    await cog.create(ctx, "Will it happen?", "official ruling", closes, liquidity)
    with cog.db.session(Market) as session:
        return session.query(Market).order_by(Market.id.desc()).first().id


async def close_markets(cog, clock, days=2):
    """Move time past the close date and let the scheduler flip OPEN markets to CLOSED."""
    clock.advance(days=days)
    await cog.tick()
