import sys
import os
import pytest
import mock

# allow for importing modules in the tests directory
sys.path.append(os.path.dirname(__file__))

# unify the module import scheme between src and tst
sys.path.insert(0, os.path.abspath(os.path.join("..", "duckbot", "duckbot")))


@pytest.fixture(autouse=True)
def async_mock_await_fix():
    """Make it so @mock.patch works for async methods."""

    async def async_magic():
        """This method's __await__ is used to hack mock awaits. No implementation needed."""
        pass

    mock.MagicMock.__await__ = lambda x: async_magic().__await__()
    yield
