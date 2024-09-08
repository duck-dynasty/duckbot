from dataclasses import dataclass
from functools import reduce
from math import isclose

from discord import Embed

from .factory import Factory
from .item import Item
from .rates import Rates
from .recipe import ModifiedRecipe, Recipe


def num_str(x: float) -> str:
    return round(x, 4)


def rate_str(rate: tuple[Item, float]) -> str:
    return f"{num_str(rate[1])} {rate[0]}"


def rates_str(rates: Rates) -> str:
    return " + ".join([rate_str(rate) for rate in rates.items()])


def factory_embed(factory: Factory) -> Embed:
    embed = Embed()

    power_shards = [] if factory.power_shards <= 0 else [f"{factory.power_shards} **Power Shard**"]
    sloops = [] if factory.sloops <= 0 else [f"{factory.sloops} **Somersloop**"]
    inputs = "\n".join([rate_str(rate) for rate in factory.inputs.items()] + power_shards + sloops)
    embed.add_field(name="Inputs", value=inputs if inputs else "N/A")

    target = "\n".join([rate_str(rate) for rate in factory.targets.items()]) if factory.targets else "N/A"
    embed.add_field(name="Target", value=target)

    maxify = "\n".join([str(item) for item in factory.maximize]) if factory.maximize else "N/A"
    embed.add_field(name="Maximize", value=maxify)

    embed.add_field(name="Recipe Bank", value=factory.recipe_bank)
    embed.add_field(name="Recipe Includes", value="\n".join(factory.include_recipes) if factory.include_recipes else "N/A")
    embed.add_field(name="Recipe Excludes", value="\n".join(factory.exclude_recipes) if factory.exclude_recipes else "N/A")

    return embed


def solution_embed(solution: dict[ModifiedRecipe, float]) -> Embed:
    embed = Embed()

    for recipe, num in solution.items():
        embed.add_field(name=recipe.original_recipe.name, value=f"{num_str(num)} {recipe.building}\n{inout_str(recipe.inputs, recipe.outputs, num)}", inline=False)

    summary = solution_summary(solution)
    embed.set_footer(text=f"{inout_str(summary.inputs, summary.outputs)}")
    return embed


def inout_str(inputs: dict[Item, float] | Rates, outputs: dict[Item, float] | Rates, scale_factor: float = 1.0) -> str:
    inputs = rates_str(scale_rates(inputs, scale_factor))
    output = rates_str(scale_rates(outputs, scale_factor))
    return f"{inputs} -> {output}"


def scale_rates(rates: dict[Item, float] | Rates, scale_factor: float) -> dict[Item, float]:
    return dict((k, scale_factor * v) for k, v in rates.items())


@dataclass
class SolutionSummary:
    inputs: dict[Item, float]
    outputs: dict[Item, float]


def solution_summary(solution: dict[Recipe, float]) -> SolutionSummary:
    inputs = reduce(sum_by_item, [scale_rates(r.inputs, -v) for r, v in solution.items()], dict())
    outputs = reduce(sum_by_item, [scale_rates(r.outputs, v) for r, v in solution.items()], dict())
    totals = sum_by_item(inputs, outputs)
    return SolutionSummary(
        inputs=dict((k, -v) for k, v in totals.items() if v < 0 and not isclose(v, 0, abs_tol=1e-4)),
        outputs=dict((k, v) for k, v in totals.items() if v > 0 and not isclose(v, 0, abs_tol=1e-4)),
    )


def sum_by_item(lhs: dict[Item, float], rhs: dict[Item, float]) -> dict[Item, float]:
    return dict((item, lhs.get(item, 0) + rhs.get(item, 0)) for item in Item if (item in lhs or item in rhs))
