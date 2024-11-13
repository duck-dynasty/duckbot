import sys
from itertools import groupby
from math import isclose
from typing import List

from .item import Item
from .rates import Rates
from .recipe import Recipe
from .recipe import all as all_recipes
from .recipe import default

map_limits = {
    Item.Bauxite: 12_300,
    Item.CateriumOre: 15_000,
    Item.Coal: 42_300,
    Item.CopperOre: 36_900,
    Item.CrudeOil: 12_600,
    Item.IronOre: 92_100,
    Item.Limestone: 69_900,
    Item.NitrogenGas: 12_000,
    Item.RawQuartz: 13_500,
    Item.Sam: 10_200,
    Item.Sulfur: 10_800,
    Item.Uranium: 2_100,
    Item.Water: sys.maxsize,
    Item.Somersloop: 106,
    Item.Leaves: sys.maxsize,
    Item.Wood: sys.maxsize,
    Item.Mycelia: sys.maxsize,
    Item.HogRemains: sys.maxsize,
    Item.HatcherRemains: sys.maxsize,
    Item.SpitterRemains: sys.maxsize,
    Item.StingerRemains: sys.maxsize,
    Item.ExcitedPhotonicMatter: sys.maxsize,
}


def unit_inputs(item: Item, recipe: Recipe) -> Rates:
    """Returns the input Rates for the recipe when the item output from the recipe is 1/min."""
    return recipe.inputs * (1.0 / recipe.outputs.get(item, 1.0))


def default_weights() -> dict[Item, float]:
    """Determines item weights (costs) based on default recipes only, and raw resource availability."""
    inputs_by_item = {i: next((unit_inputs(i, r) for r in default() if r.name == str(i)), Rates()) for i in Item}
    # manually add items which would have no recipe otherwise
    inputs_by_item[Item.FicsiteIngot] = next(unit_inputs(Item.FicsiteIngot, r) for r in default() if r.name == "FicsiteIngot#Iron")
    inputs_by_item[Item.PowerShard] = next(unit_inputs(Item.PowerShard, r) for r in default() if r.name == "SyntheticPowerShard")
    inputs_by_item[Item.TurboRifleAmmo] = next(unit_inputs(Item.TurboRifleAmmo, r) for r in default() if r.name == f"{Item.TurboRifleAmmo}#Blender")
    inputs_by_item[Item.UraniumWaste] = next(unit_inputs(Item.UraniumWaste, r) for r in default() if r.name == f"NuclearPowerPlant#{Item.UraniumFuelRod}")
    inputs_by_item[Item.PlutoniumWaste] = next(unit_inputs(Item.PlutoniumWaste, r) for r in default() if r.name == f"NuclearPowerPlant#{Item.PlutoniumFuelRod}")
    inputs_by_item[Item.HeavyOilResidue] = next(unit_inputs(Item.HeavyOilResidue, r) for r in all_recipes() if r.name == str(Item.HeavyOilResidue))
    inputs_by_item[Item.PolymerResin] = next(unit_inputs(Item.PolymerResin, r) for r in all_recipes() if r.name == str(Item.PolymerResin))
    inputs_by_item[Item.Fabric] = next(unit_inputs(Item.Fabric, r) for r in all_recipes() if r.name == "PolyesterFabric")
    inputs_by_item[Item.PortableMiner] = next(unit_inputs(Item.PortableMiner, r) for r in all_recipes() if r.name == "AutomatedMiner")

    weights = {i: 1.0 / total for i, total in map_limits.items()}
    adjusted = True
    while adjusted:
        adjusted = False
        for item in Item:
            if item not in weights:
                if all(i in weights for i, _ in inputs_by_item[item].items()):
                    weights[item] = sum(r * weights[i] for i, r in inputs_by_item[item].items())
                    adjusted = True

    return weights


def alternate_weights() -> dict[Item, float]:
    """Determines item weights (costs) based on the cheapest possible cost given all alternates."""
    recipes_by_input = _recipes_by_input_item()
    weights = {item: 1.0 / limit for item, limit in map_limits.items()}
    # manually add recycling chain, since it is an iterative process which won't resolve with this approach
    weights[Item.Plastic] = (1 / 3 * weights[Item.CrudeOil]) + (10 / 9 * weights[Item.Water])
    weights[Item.Rubber] = (1 / 3 * weights[Item.CrudeOil]) + (10 / 9 * weights[Item.Water])

    def propagate(item: Item):
        """For each recipe where item is an input, calculate the new weight of that recipe's output."""
        for recipe in recipes_by_input.get(item, []):
            if all(i in weights for i in recipe.inputs.keys()):
                for out in recipe.outputs.keys():
                    rates = unit_inputs(out, recipe)
                    new_weight = sum(weights[i] * rate for i, rate in rates.items())
                    if out not in weights or new_weight < weights[out]:
                        weights[out] = new_weight
                        propagate(out)

    for item in Item:
        propagate(item)
    return weights


def _recipes_by_input_item() -> dict[Item, List[Recipe]]:
    recipe_inputs = sorted(((recipe, item) for recipe in all_recipes() for item, _ in recipe.inputs.items()), key=lambda r: r[1])
    return {item: [r[0] for r in recipes] for item, recipes in groupby(recipe_inputs, lambda r: r[1])}


def minmax_weights():
    item_weights = default_weights()
    max_weight = max(item_weights.values())
    min_weight = min(v for v in item_weights.values() if not isclose(v, 0, abs_tol=1e-6))

    # fudge auxiliary items to avoid them unless asked
    item_weights[Item.MwPower] = max_weight
    item_weights[Item.AwesomeTicketPoints] = max_weight

    scale_factor = 1.0 / max_weight * 10
    scaled = {i: scale_factor * v for i, v in item_weights.items()}
    all_items = {i: scale_factor * max_weight * 100 for i in Item}
    return all_items | scaled, scale_factor * max_weight, scale_factor * min_weight
