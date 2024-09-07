import itertools
from functools import reduce
from math import ceil
from typing import List

from mip import CONTINUOUS, INF, INTEGER, MAXIMIZE, LinExpr, Model, Var

from .factory import Factory
from .item import Item
from .recipe import Recipe

zero = LinExpr(const=0)


def optimize(factory: Factory) -> dict[Recipe, float]:
    model = Model(sense=MAXIMIZE)
    model.verbose = 0

    use_recipes = [model.add_var(lb=0, ub=INF) for _ in factory.recipes]

    def cost(recipe: Recipe, use: Var | LinExpr) -> dict[Item, LinExpr]:
        costs = dict((item, -use * rate) for item, rate in recipe.inputs.items())
        income = dict((item, use * rate) for item, rate in recipe.outputs.items())
        return costs, income

    recipe_costs = [sum_by_item(*cost(r, v)) for r, v in zip(factory.recipes, use_recipes)]
    aggregation = reduce(sum_by_item, recipe_costs, dict())

    initial_conditions = sum_by_item(factory.inputs, dict((i, -r) for i, r in factory.targets.items()))
    constraints = sum_by_item(initial_conditions, aggregation)

    for c in constraints.values():
        model.add_constr(c >= 0)

    model.objective = sum([c for i, c in constraints.items() if i in factory.maximize])
    model.optimize()

    return dict((r, float(v.x)) for r, v in zip(factory.recipes, use_recipes) if v.x is not None and v.x > 0)


def sum_by_item(lhs: dict[Item, LinExpr], rhs: dict[Item, LinExpr]) -> dict[Item, LinExpr]:
    return dict((item, lhs.get(item, zero) + rhs.get(item, zero)) for item in Item if (item in lhs or item in rhs))


def recipe_explosion_optimize(factory: Factory) -> dict[Recipe, float]:
    model = Model(sense=MAXIMIZE)
    model.threads = -1
    # model.verbose = 0
    recipes = recipe_explosion(factory.recipes, factory.power, factory.sloops)

    use_recipe = [model.add_var(name=r.name, lb=0, ub=INF if r.name.endswith("#0#0") else factory.sloops, var_type=CONTINUOUS if r.name.endswith("#0#0") else INTEGER) for r in recipes]

    def cost(recipe: Recipe, use: Var | LinExpr) -> dict[Item, LinExpr]:
        costs = dict((item, -use * rate) for item, rate in recipe.inputs.items())
        income = dict((item, use * rate) for item, rate in recipe.outputs.items())
        return costs, income

    recipe_costs = [sum_by_item(*cost(r, v)) for r, v in zip(recipes, use_recipe)]
    aggregation = reduce(sum_by_item, recipe_costs, dict())
    initial_conditions = sum_by_item(factory.inputs, dict((i, -r) for i, r in factory.targets.items()))
    amount_by_item = sum_by_item(initial_conditions, aggregation)

    for c in amount_by_item.values():
        model.add_constr(c >= 0)

    used_shards = sum([int(r.name.split("#")[1]) * v for r, v in zip(recipes, use_recipe)])
    used_sloops = sum([int(r.name.split("#")[2]) * v for r, v in zip(recipes, use_recipe)])
    model.add_constr(used_shards <= factory.power)
    model.add_constr(used_sloops <= factory.sloops)

    maximize_items = sum([c for i, c in amount_by_item.items() if i in factory.maximize])
    model.objective = 10000 * maximize_items - 3 * used_shards - 10 * used_sloops
    model.optimize()

    return dict((r, float(v.x)) for r, v in zip(recipes, use_recipe) if v.x is not None and v.x > 0)


def recipe_explosion(recipes: List[Recipe], max_shards: int, max_sloops: int) -> List[Recipe]:
    def scale(recipe: Recipe, shards: int, sloops: int) -> Recipe:
        shard_scale = 1.0 + shards * 0.5 if recipe.building.max_shards > 0 else 1.0
        sloop_scale = 1.0 + float(sloops) / recipe.building.max_sloop if recipe.building.max_sloop > 0 else 1.0
        return Recipe(f"{recipe.name}#{shards}#{sloops}", recipe.building, recipe.inputs * shard_scale, recipe.outputs * shard_scale * sloop_scale)

    non_sloopers = [scale(recipe, 0, 0) for recipe in recipes if recipe.building.max_sloop <= 0]
    zero_sloop = [scale(recipe, 0, 0) for recipe in recipes if recipe.building.max_sloop > 0]
    nonzero_sloop = [
        scale(recipe, power, sloops)
        for recipe in recipes
        for power, sloops in itertools.product(range(0, min(max_shards, recipe.building.max_shards) + 1), range(1, min(max_sloops, recipe.building.max_sloop) + 1))
    ]
    return non_sloopers + zero_sloop + nonzero_sloop


def building_track_optimize(factory: Factory) -> dict[Recipe, float]:
    model = Model(sense=MAXIMIZE)

    return dict()
