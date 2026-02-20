import pytest

from duckbot.cogs.games.satisfy.building import Building
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates
from duckbot.cogs.games.satisfy.recipe import (
    ModifiedRecipe,
    Recipe,
    all,
    can,
    tank,
    uncan,
    untank,
)


@pytest.mark.parametrize("name", ["", "name", "another example"])
@pytest.mark.parametrize("building", Building)
def test_hash_is_name(name: str, building: Building):
    assert hash(Recipe(name, building, Rates(), Rates())) == hash(name)


def test_recipes_have_unique_names():
    names = [r.name for r in all()]
    assert len(set(names)) == len(names)


def test_can_adds_empty_canister_inputs():
    recipe = can("thing", Item.Water * 180 >> Item.PackagedWater * 60)
    assert recipe.inputs == Item.Water * 180 + Item.EmptyCanister * 60
    assert recipe.outputs == Item.PackagedWater * 60


def test_uncan_adds_empty_canister_outputs():
    recipe = uncan("thing", Item.PackagedWater * 60 >> Item.Water * 180)
    assert recipe.inputs == Item.PackagedWater * 60
    assert recipe.outputs == Item.Water * 180 + Item.EmptyCanister * 60


def test_tank_adds_empty_tanks_inputs():
    recipe = tank("thing", Item.Water * 120 >> Item.PackagedWater * 60)
    assert recipe.inputs == Item.Water * 120 + Item.EmptyFluidTank * 60
    assert recipe.outputs == Item.PackagedWater * 60


def test_untank_adds_empty_tanks_outputs():
    recipe = untank("thing", Item.PackagedWater * 60 >> Item.Water * 120)
    assert recipe.inputs == Item.PackagedWater * 60
    assert recipe.outputs == Item.Water * 120 + Item.EmptyFluidTank * 60


def test_capped_shard_scale_within_limits_is_unchanged():
    recipe = Recipe("test", Building.Assembler, inputs=Item.IronOre * 10, outputs=Item.IronIngot * 5)
    r = ModifiedRecipe(recipe, power_shards=3, sloops=2)
    assert r.capped_shard_scale == pytest.approx(2.5)


def test_capped_shard_scale_fluid_output_exceeds_pipe_limit():
    recipe = Recipe("test", Building.Manufacturer, inputs=Rates(), outputs=Item.Water * 125)
    r = ModifiedRecipe(recipe, power_shards=3, sloops=4)
    assert r.capped_shard_scale == pytest.approx(2.4)


def test_capped_shard_scale_solid_input_exceeds_belt_limit():
    recipe = Recipe("test", Building.Assembler, inputs=Item.IronOre * 600, outputs=Rates())
    r = ModifiedRecipe(recipe, power_shards=3, sloops=0)
    assert r.capped_shard_scale == pytest.approx(2.0)


def test_capped_shard_scale_aux_output_is_not_capped():
    recipe = Recipe("test", Building.Manufacturer, inputs=Rates(), outputs=Item.MwPower * 10000)
    r = ModifiedRecipe(recipe, power_shards=3, sloops=0)
    assert r.capped_shard_scale == pytest.approx(2.5)
