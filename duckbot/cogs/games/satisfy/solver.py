import itertools
from functools import reduce
from math import isclose
from typing import Callable, List

from mip import INF, INTEGER, LinExpr, Model, Var, maximize, xsum

from .factory import Factory
from .item import Item
from .recipe import ModifiedRecipe, Recipe

zero = LinExpr(const=0)


def optimize(factory: Factory) -> dict[ModifiedRecipe, float]:
    model = Model()
    model.threads = -1
    model.verbose = 0

    recipes = modify_recipes(factory.recipes, factory.power_shards, factory.sloops)

    use_recipe = [model.add_var(name=r.name, lb=0, ub=factory.sloops / r.sloops if r.sloops > 0 else INF) for r in recipes]

    amount_by_item = amount_by_item_expressions(factory, recipes, use_recipe)
    items_must_be_non_negative(model, amount_by_item)

    used_power_shards = power_shards_used(model, factory, recipes, use_recipe)
    used_sloops = sloops_used(model, factory, recipes, use_recipe)

    maximize_items = xsum([amount for i, amount in amount_by_item.items() if i in factory.maximize])
    model.objective = maximize(
        10000 * maximize_items  # prioritize maximizing requested items
        - 3 * used_power_shards  # minimize power shard usage
        - 10 * used_sloops  # minimize sloop usage
        - xsum(use_recipe)  # minimize recipe usage
    )
    model.optimize()

    return dict((r, round(float(v.x), 4)) for r, v in zip(recipes, use_recipe) if v.x is not None and v.x > 0 and not isclose(float(v), 0, abs_tol=1e-4))


def modify_recipes(recipes: List[Recipe], max_shards: int, max_sloops: int) -> List[ModifiedRecipe]:
    """Creates recipes which are scaled by power shards and sloops. The recipes are always scaled to max clock
    speed which the power shards allow, then the solver will be allowed to underclock them as needed."""
    non_sloopers = [ModifiedRecipe(recipe, 0, 0) for recipe in recipes if recipe.building.max_sloop <= 0]
    zero_sloop = [ModifiedRecipe(recipe, 0, 0) for recipe in recipes if recipe.building.max_sloop > 0]
    nonzero_sloop = [
        ModifiedRecipe(recipe, power, sloops)
        for recipe in recipes
        for power, sloops in itertools.product(range(0, min(max_shards, recipe.building.max_shards) + 1), range(1, min(max_sloops, recipe.building.max_sloop) + 1))
    ]
    return non_sloopers + zero_sloop + nonzero_sloop


def amount_by_item_expressions(factory: Factory, recipes: List[ModifiedRecipe], use_recipe: List[Var]) -> dict[Item, LinExpr]:
    """Sums up all items produced and consumed by the factory based on the number of recipes used in the model.
    The inputs to the factory are a constant positive modify to the number of items available, and the factory
    targets are negative modifiers. Eg, for a IronOre >> IronPlate factory,
    TotalIronOre = IronOreInput - x1*30*RecipeIronIngot - other recipes...
    TotalIronIngot = 0 + x1*30*RecipeIronIngot - x2*30*RecipeIronPlate + other recipes...
    TotalIronPlate = -TargetIronPlate + x2*20*RecipeIronPlate + other recipes...
    """

    def cost(recipe: ModifiedRecipe, use: Var | LinExpr) -> dict[Item, LinExpr]:
        costs = dict((item, -use * rate) for item, rate in recipe.inputs.items())
        income = dict((item, use * rate) for item, rate in recipe.outputs.items())
        return costs, income

    recipe_costs = [sum_by_item(*cost(r, v)) for r, v in zip(recipes, use_recipe)]
    initial_conditions = sum_by_item(factory.inputs, dict((i, -r) for i, r in factory.targets.items()))
    return reduce(sum_by_item, recipe_costs, initial_conditions)


def sum_by_item(lhs: dict[Item, LinExpr], rhs: dict[Item, LinExpr]) -> dict[Item, LinExpr]:
    return dict((item, lhs.get(item, zero) + rhs.get(item, zero)) for item in Item if (item in lhs or item in rhs))


def items_must_be_non_negative(model: Model, amount_by_item: dict[Item, LinExpr]):
    for amount in amount_by_item.values():
        model.add_constr(amount >= 0)


def power_shards_used(model: Model, factory: Factory, recipes: List[ModifiedRecipe], use_recipe: List[Var]) -> LinExpr:
    return limited_item_used(model, "power", factory.power_shards, recipes, use_recipe, lambda r: r.power_shards)


def sloops_used(model: Model, factory: Factory, recipes: List[ModifiedRecipe], use_recipe: List[Var]) -> LinExpr:
    return limited_item_used(model, "sloop", factory.sloops, recipes, use_recipe, lambda r: r.sloops)


def limited_item_used(model: Model, item: str, limit: int, recipes: List[ModifiedRecipe], use_recipe: List[Var], amount_recipe_uses: Callable[[ModifiedRecipe], int]) -> LinExpr:
    """Power shards and sloopers are a limited, indivisible item that can be put into machines. This sums up the
    number of shards or sloops used based on recipe usage. The number of items used is `ceil(num_recipe)`,
    and the total of those must be constrainted by the amount available to the factory."""
    item_cost = [
        (
            r,
            v,
            model.add_var(name=f"{v.name}#{item}", var_type=INTEGER),
        )
        for r, v in zip(recipes, use_recipe)
        if r.sloops > 0
    ]

    for _, v, p in item_cost:
        model.add_constr(p >= v)
        model.add_constr(p <= v + 1 - 0.00001)  # v <= p < v+1, ie, p = ceil(v)

    total_used_item = xsum([amount_recipe_uses(r) * p for r, _, p in item_cost])
    model.add_constr(total_used_item <= limit)
    return total_used_item
