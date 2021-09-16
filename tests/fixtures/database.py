from unittest import mock

import pytest


@pytest.fixture
@mock.patch("sqlalchemy.orm.session.Session")
def session(s):
    """Returns a mock ORM session."""
    return s


@pytest.fixture
@mock.patch("duckbot.db.Database")
def db(d, session):
    """Returns a database with a stubbed session value."""
    d.session.return_value.__enter__.return_value = session
    return d
