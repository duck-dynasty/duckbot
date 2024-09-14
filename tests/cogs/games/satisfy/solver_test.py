from typing import Set

import pytest

from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates
from duckbot.cogs.games.satisfy.recipe import ModifiedRecipe, all, default, raw
from duckbot.cogs.games.satisfy.solver import optimize

all_no_raw = [r for r in all() if r.name not in [x.name for x in raw()]]
default_no_raw = [r for r in default() if r.name not in [x.name for x in raw()]]


def approx(x):
    return pytest.approx(x, abs=1e-4)


def factory(*, input: Rates, target: Rates = Rates(), maximize: Set[Item] = set(), recipes=all_no_raw, power_shards: int = 0, sloops: int = 0):
    return Factory(inputs=input, targets=target, maximize=maximize, power_shards=power_shards, sloops=sloops, recipes=recipes)


def test_optimize_empty_factory_returns_empty():
    assert optimize(factory(input=Rates())) == dict()


def test_optimize_trivial_factory_returns_empty():
    rates = Item.IronOre * 30
    assert optimize(factory(input=rates, target=rates)) == dict()


def test_optimize_infeasible_returns_none():
    f = factory(input=Item.IronOre * 30, target=Item.IronIngot * 31, recipes=all_no_raw)
    assert optimize(f) is None


def test_optimize_simple_factory_target_returns_recipe():
    f = factory(input=Item.IronOre * 30, target=Item.IronIngot * 30, recipes=default())
    recipe = recipe_by_name("IronIngot")
    assert optimize(f) == dict([(recipe, approx(1))])


def test_optimize_simple_factory_maximize_returns_recipe():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronIngot]), recipes=default_no_raw)
    recipe = recipe_by_name("IronIngot")
    assert optimize(f) == dict([(recipe, approx(1))])


def test_optimize_simple_sloop_target_returns_recipe():
    f = factory(input=Item.IronOre * 30, target=Item.IronIngot * 60, sloops=1, recipes=default_no_raw)
    recipe = recipe_by_name("IronIngot", sloops=1)
    assert optimize(f) == dict([(recipe, approx(1))])


def test_optimize_simple_sloop_maximize_returns_recipe():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronIngot]), sloops=1, recipes=default_no_raw)
    recipe = recipe_by_name("IronIngot", sloops=1)
    assert optimize(f) == dict([(recipe, approx(1))])


def test_optimize_create_resources_returns_target():
    f = factory(input=Rates(), target=Item.IronIngot * 30, recipes=default())
    ore = recipe_by_name("IronOre")
    ingot = recipe_by_name("IronIngot")
    assert optimize(f) == dict([(ore, approx(0.5)), (ingot, approx(1))])


def test_optimize_two_step_returns_chain():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronPlate]), recipes=default_no_raw)
    ignot = recipe_by_name("IronIngot")
    plate = recipe_by_name("IronPlate")
    assert optimize(f) == dict([(ignot, approx(1)), (plate, approx(1))])


def test_optimize_two_step_single_sloop_returns_chain():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronPlate]), sloops=1, recipes=default_no_raw)
    ignot = recipe_by_name("IronIngot")
    plate = recipe_by_name("IronPlate", sloops=1)
    assert optimize(f) == dict([(ignot, approx(1)), (plate, approx(1))])


def test_optimize_two_step_many_sloop_returns_chain():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronPlate]), sloops=10, recipes=default_no_raw)
    ignot = recipe_by_name("IronIngot", sloops=1)
    plate = recipe_by_name("IronPlate", sloops=1)
    assert optimize(f) == dict([(ignot, approx(1)), (plate, approx(2))])


def test_optimize_two_step_many_sloop_and_power_shards_returns_chain():
    f = factory(input=Item.IronOre * 30, maximize=set([Item.IronPlate]), sloops=10, power_shards=10, recipes=default_no_raw)
    ignot = recipe_by_name("IronIngot", sloops=1)
    plate = recipe_by_name("IronPlate", sloops=1, power_shards=2)
    assert optimize(f) == dict([(ignot, approx(1)), (plate, approx(1))])


def test_optimize_fluid_excess_is_made_sinkable():
    f = factory(input=Item.CrudeOil * 30, target=Item.Plastic * 20, recipes=default())
    plastic = recipe_by_name("Plastic")
    coke = recipe_by_name("PetroleumCoke")
    assert optimize(f) == dict([(plastic, approx(1)), (coke, approx(0.25))])


def test_optimize_recycled_bois_returns_chain():
    f = factory(input=Item.Water * 90 + Item.CrudeOil * 27, target=Item.Plastic * 81, recipes=[r for r in all_no_raw if r.name != "DilutedFuel"])
    goo = recipe_by_name("HeavyOilResidue")
    dilute = recipe_by_name("DilutedPackagedFuel")
    wudder = recipe_by_name("PackagedWater")
    fuel = recipe_by_name("UnpackageFuel")
    residual = recipe_by_name("ResidualRubber")
    plastic = recipe_by_name("RecycledPlastic")
    rubber = recipe_by_name("RecycledRubber")
    assert optimize(f) == dict(
        [
            (goo, approx(0.9)),
            (dilute, approx(1.2)),
            (wudder, approx(1.2)),
            (fuel, approx(1.2)),
            (residual, approx(0.45)),
            (plastic, approx(1.7)),
            (rubber, approx(0.7)),
        ]
    )


def recipe_by_name(name: str, power_shards: int = 0, sloops: int = 0) -> ModifiedRecipe:
    return ModifiedRecipe(next(r for r in all() if r.name == name), power_shards, sloops)
