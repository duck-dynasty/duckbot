import locale

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_locale():
    """Initializes the standard library locale to use the default OS locale."""
    locale.setlocale(locale.LC_ALL, "")
