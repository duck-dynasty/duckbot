import pytest

from duckbot.cogs.games.satisfy.building import Building
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates
from duckbot.cogs.games.satisfy.recipe import Recipe, can, uncan


@pytest.mark.parametrize("name", ["", "name", "another example"])
@pytest.mark.parametrize("building", Building)
def test_hash_is_name(name: str, building: Building):
    assert hash(Recipe(name, building, Rates(), Rates())) == hash(name)


def test_can_adds_empty_canister_inputs():
    recipe = can("thing", Item.Water * 60 >> Item.PackagedWater * 60)
    assert recipe.inputs == Item.Water * 60 + Item.EmptyCanister * 60
    assert recipe.outputs == Item.PackagedWater * 60


def test_uncan_adds_empty_canister_outputs():
    recipe = uncan("thing", Item.PackagedWater * 60 >> Item.Water * 60)
    assert recipe.inputs == Item.PackagedWater * 60
    assert recipe.outputs == Item.Water * 60 + Item.EmptyCanister * 60
