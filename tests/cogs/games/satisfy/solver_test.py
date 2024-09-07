from pytest import approx

from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rate import Rates
from duckbot.cogs.games.satisfy.recipe import ModifiedRecipe, all
from duckbot.cogs.games.satisfy.solver import optimize


def test_optimize_empty_factory_returns_empty():
    assert optimize(Factory(Rates(), all(), Rates(), set())) == dict()


def test_optimize_trivial_factory_returns_empty():
    factory = Factory(Rates([Item.IronOre * 30]), all(), Rates([Item.IronOre * 30]), set())
    assert optimize(factory) == dict()


def test_optimize_infeasible_returns_empty():
    factory = Factory(Rates([Item.IronOre * 30]), all(), Rates([Item.IronIngot * 31]), set())
    assert optimize(factory) == dict()


def test_optimize_simple_factory_target_returns_recipe():
    factory = Factory(Rates([Item.IronOre * 30]), all(), Rates([Item.IronIngot * 30]), set())
    recipe = recipe_by_name("IronIngot")
    assert optimize(factory) == dict([(recipe, 1)])


def test_optimize_simple_factory_maximize_returns_recipe():
    factory = Factory(Rates([Item.IronOre * 30]), all(), Rates(), set([Item.IronIngot]))
    recipe = recipe_by_name("IronIngot")
    assert optimize(factory) == dict([(recipe, 1)])


def test_optimize_two_step_returns_chain():
    factory = Factory(Rates([Item.IronOre * 30]), all(), Rates(), set([Item.IronPlate]))
    ignot = recipe_by_name("IronIngot")
    plate = recipe_by_name("IronPlate")
    assert optimize(factory) == dict([(ignot, 1), (plate, 1)])


def test_optimize_recycled_bois_returns_chain():
    factory = Factory(inputs=Item.Water * 90 + Item.CrudeOil * 27, targets=Rates([Item.Plastic * 81]), recipes=[r for r in all() if r.name != "DilutedFuel"], maximize=set())
    goo = recipe_by_name("HeavyOilResidue")
    dilute = recipe_by_name("DilutedPackagedFuel")
    wudder = recipe_by_name("PackagedWater")
    fuel = recipe_by_name("UnpackageFuel")
    residual = recipe_by_name("ResidualRubber")
    plastic = recipe_by_name("RecycledPlastic")
    rubber = recipe_by_name("RecycledRubber")
    assert optimize(factory) == dict(
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


def recipe_by_name(name: str) -> ModifiedRecipe:
    return ModifiedRecipe(next(r for r in all() if r.name == name), 0, 0)
