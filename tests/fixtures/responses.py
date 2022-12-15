import pytest
import responses as resp


@pytest.fixture
def responses() -> resp.RequestsMock:
    with resp.RequestsMock() as r:
        yield r
