from functools import reduce

from mip import INF, MAXIMIZE, LinExpr, Model, Var

from .factory import Factory
from .item import Item
from .recipe import Recipe

zero = LinExpr(const=0)


def optimize(factory: Factory) -> dict[Recipe, float]:
    model = Model(sense=MAXIMIZE)
    model.verbose = 0

    use_recipes = [model.add_var(f"Recipe_{r.name}", lb=0, ub=INF) for r in factory.recipes]

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

    model.objective = zero + sum([c for i, c in constraints.items() if i in factory.maximize])
    model.optimize()

    return dict((r, float(v.x)) for r, v in zip(factory.recipes, use_recipes) if v.x is not None and v.x > 0)


def sum_by_item(lhs: dict[Item, LinExpr], rhs: dict[Item, LinExpr]) -> dict[Item, LinExpr]:
    return dict((item, lhs.get(item, zero) + rhs.get(item, zero)) for item in Item if (item in lhs or item in rhs))
