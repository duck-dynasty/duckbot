from typing import Set

import pytest

from duckbot.cogs.games.satisfy.building import Building
from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates
from duckbot.cogs.games.satisfy.recipe import (
    ModifiedRecipe,
    Recipe,
    all,
    as_slooped,
    default,
    raw,
)
from duckbot.cogs.games.satisfy.solver import optimize

all_no_raw = [r for r in all() if r.name not in [x.name for x in raw()]]
default_no_raw = [r for r in default() if r.name not in [x.name for x in raw()]]
default_with_raw = default() + raw()


def approx(x):
    return pytest.approx(x, abs=1e-4)


def factory(*, input: Rates, target: Rates = Rates(), maximize: Set[Item] = set(), recipes=all_no_raw, limits={}, power_shards: int = 0, sloops: int = 0):
    return Factory(inputs=input, targets=target, maximize=maximize, power_shards=power_shards, sloops=sloops, recipes=[x for r in recipes for x in as_slooped(r)], limits=limits)


def test_optimize_empty_factory_returns_empty():
    assert optimize(factory(input=Rates())) == dict()


def test_optimize_trivial_factory_returns_empty():
    rates = Item.IronOre * 30
    assert optimize(factory(input=rates, target=rates)) == dict()


def test_optimize_infeasible_returns_none():
    f = factory(input=Item.IronOre * 30, target=Item.IronIngot * 31, recipes=all_no_raw)
    assert optimize(f) is None


def test_optimize_simple_factory_target_returns_recipe():
    f = factory(input=Item.IronOre * 30, target=Item.IronIngot * 30, recipes=default_with_raw)
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


def test_optimize_limit_recipe():
    f = factory(input=Item.IronOre * 30 + Item.Water * 1000, maximize=set([Item.IronIngot]), recipes=all_no_raw, limits={recipe_by_name("PureIronIngot"): 0.5})
    pure = recipe_by_name("PureIronIngot")
    smelt = recipe_by_name("IronIngot")
    assert optimize(f) == dict([(pure, approx(0.5)), (smelt, approx(0.41666))])


def test_optimize_limit_boosted_recipe():
    f = factory(input=Item.IronOre * 30 + Item.Water * 1000, maximize=set([Item.IronIngot]), recipes=default_no_raw, limits={recipe_by_name("PureIronIngot", 1, 2): 0.5}, power_shards=10, sloops=2)
    pure = recipe_by_name("PureIronIngot")
    pure_slooped = recipe_by_name("PureIronIngot", 1, 2)
    f.recipes = f.recipes + [pure, pure_slooped]  # exclude other pure irons so it's forced to use unslooped
    assert optimize(f) == dict([(pure_slooped, approx(0.5)), (pure, approx(3.75 / 35))])


def test_optimize_create_resources_returns_target():
    f = factory(input=Rates(), target=Item.IronIngot * 30, recipes=default_with_raw)
    ore = recipe_by_name("IronOre")
    ingot = recipe_by_name("IronIngot")
    assert optimize(f) == dict([(ore, approx(0.5)), (ingot, approx(1))])


def test_optimize_create_resources_minimal_inputs_used():
    f = factory(input=Rates(), target=Item.ReinforcedIronPlate * 5.625, recipes=default_no_raw + [r for r in all() if r.name in ["IronOre", "IronWire", "StitchedIronPlate"]])
    ore = recipe_by_name("IronOre")
    ingot = recipe_by_name("IronIngot")
    wire = recipe_by_name("IronWire")
    plate = recipe_by_name("IronPlate")
    super_plate = recipe_by_name("StitchedIronPlate")
    assert optimize(f) == dict(
        [
            (ore, approx(48.958 / 60.0)),
            (ingot, approx(48.958 / 30.0)),
            (wire, approx(1.0 + 2.0 / 3.0)),
            (plate, approx(18.75 / 20.0)),
            (super_plate, approx(1)),
        ]
    )


def test_optimize_create_resources_with_inputs_minimizes_inputs_used():
    f = factory(input=Item.IronIngot * 30, target=Item.IronPlate * 40, recipes=default_with_raw)
    ore = recipe_by_name(Item.IronOre)
    ingot = recipe_by_name(Item.IronIngot)
    plate = recipe_by_name(Item.IronPlate)
    assert optimize(f) == dict(
        [
            (ore, approx(30.0 / 60.0)),
            (ingot, approx(1.0)),
            (plate, approx(2.0)),
        ]
    )


def test_optimize_create_resources_with_inputs_issue_995():
    f = factory(input=Item.CrystalOscillator * 1, target=Item.RadioControlUnit * 3, recipes=all())
    crystal = recipe_by_name("InsulatedCrystalOscillator")
    assert optimize(f)[crystal] == approx(0.2667)  # makes 0.5 extra only


def test_optimize_create_expensive_resources_with_inputs():
    f = factory(input=Item.CrystalOscillator * 1, target=Item.CrystalOscillator * 2, recipes=all())
    crystal = recipe_by_name("InsulatedCrystalOscillator")
    assert optimize(f)[crystal] == approx(0.5333)  # makes 1 extra only


@pytest.mark.skip(reason="very cheap resources are still preferred to be made")
def test_optimize_create_cheap_resources_with_inputs():
    f = factory(input=Item.Plastic * 9, target=Item.Plastic * 90, recipes=all())
    plastic = recipe_by_name("RecycledPlastic")
    for k, v in optimize(f).items():
        print(k, v)
    assert optimize(f)[plastic] == approx(1.7)  # makes 81 extra only


def test_optimize_maximize_oversupplied_minimizes_inputs_used():
    f = factory(input=Item.Coal * 120 + Item.IronOre * 120 + Item.Limestone * 270, maximize=set([Item.EncasedIndustrialBeam]), recipes=all_no_raw)
    ingot = recipe_by_name("IronIngot")
    steel = recipe_by_name("SolidSteelIngot")
    concrete = recipe_by_name("Concrete")
    pipe = recipe_by_name("SteelPipe")
    butter = recipe_by_name("EncasedIndustrialPipe")
    assert optimize(f) == dict(
        [
            (concrete, approx(6)),
            (ingot, approx(3.6)),
            (pipe, approx(5.4)),
            (butter, approx(4.5)),
            (steel, approx(2.7)),
        ]
    )


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
    f = factory(input=Item.CrudeOil * 30, target=Item.Plastic * 20, recipes=default_with_raw)
    plastic = recipe_by_name("Plastic")
    coke = recipe_by_name("PetroleumCoke")
    assert optimize(f) == dict([(plastic, approx(1)), (coke, approx(0.25))])


def test_optimize_raw_resources_are_bound_by_map_limits():
    f = factory(input=Rates(), maximize=set([Item.IronOre]), recipes=all())
    ore = recipe_by_name("IronOre")
    lime = recipe_by_name("Limestone")
    sam = recipe_by_name("Sam")
    reanimate = recipe_by_name("ReanimatedSam")
    convert = recipe_by_name("IronOre#Limestone")
    assert optimize(f) == dict(
        [
            (ore, approx(92_100.0 / 60.0)),
            (lime, approx(61_200.0 / 60.0)),
            (sam, approx(10_200.0 / 60.0)),
            (reanimate, approx(85)),
            (convert, approx(255)),
        ]
    )


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


def recipe_by_name(name: str | Item, power_shards: int = 0, sloops: int = 0) -> ModifiedRecipe:
    return ModifiedRecipe(next(r for r in all() if r.name == str(name)), power_shards, sloops)


def test_optimize_solid_input_exceeds_belt_limit():
    recipe = Recipe("test", Building.Assembler, inputs=Item.IronOre * 500, outputs=Item.IronIngot * 100)
    f = factory(input=Item.IronOre * 2400, target=Item.IronIngot * 960, recipes=[recipe], power_shards=6, sloops=4)
    assert optimize(f) == {ModifiedRecipe(recipe, 3, 2): approx(2.0)}


def test_optimize_fluid_input_exceeds_pipe_limit():
    recipe = Recipe("test", Building.Assembler, inputs=Item.Water * 250, outputs=Item.IronIngot * 100)
    f = factory(input=Item.Water * 1200, target=Item.IronIngot * 960, recipes=[recipe], power_shards=6, sloops=4)
    assert optimize(f) == {ModifiedRecipe(recipe, 3, 2): approx(2.0)}


def test_optimize_solid_output_exceeds_belt_limit():
    recipe = recipe_by_name("TurboRifleAmmo#Manufacturer").original_recipe
    f = factory(
        input=Item.RifleAmmo * 576 + Item.AluminumCasing * 72 + Item.PackagedTurbofuel * 72,
        target=Item.TurboRifleAmmo * 2400,
        recipes=[recipe],
        power_shards=6,
        sloops=8,
    )
    assert optimize(f) == {recipe_by_name("TurboRifleAmmo#Manufacturer", 3, 4): approx(2.0)}


def test_optimize_fluid_output_exceeds_pipe_limit():
    recipe = recipe_by_name("SuperpositionOscillator").original_recipe
    f = factory(
        input=Item.DarkMatterCrystal * 144 + Item.CrystalOscillator * 24 + Item.AlcladAluminumSheet * 216 + Item.ExcitedPhotonicMatter * 600,
        target=Item.SuperpositionOscillator * 48,
        recipes=[recipe],
        power_shards=6,
        sloops=8,
    )
    assert optimize(f) == {recipe_by_name("SuperpositionOscillator", 3, 4): approx(2.0)}
