import pytest

from duckbot.cogs.games.satisfy.building import Building


@pytest.mark.parametrize("building", Building)
def test_str_returns_enum_name(building: Building):
    assert str(building) == building.name


@pytest.mark.parametrize("building", Building)
def test_repr_returns_enum_name(building: Building):
    assert repr(building) == building.name
