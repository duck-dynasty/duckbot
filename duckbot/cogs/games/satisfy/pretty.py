from dataclasses import dataclass
from functools import reduce
from math import ceil, isclose
from typing import List

from discord import Embed

from duckbot.util.embeds import MAX_FIELDS

from .factory import Factory
from .item import Item
from .rates import Rates
from .recipe import ModifiedRecipe, raw


def rnd(num: float) -> float:
    return round(num, 4)


def rate_str(rate: tuple[Item, float]) -> str:
    return f"{rnd(rate[1])} {rate[0]}"


def rates_str(rates: Rates) -> str:
    return " + ".join([rate_str(rate) for rate in rates.items()])


def factory_embed(factory: Factory) -> Embed:
    embed = Embed()

    power_shards = [] if factory.power_shards <= 0 else [f"{factory.power_shards} **{Item.PowerShard}**"]
    sloops = [] if factory.sloops <= 0 else [f"{factory.sloops} **{Item.Somersloop}**"]
    inputs = "\n".join([rate_str(rate) for rate in factory.inputs.items()] + power_shards + sloops)
    embed.add_field(name="Inputs", value=inputs if inputs else "N/A")

    target = "\n".join([rate_str(rate) for rate in factory.targets.items()]) if factory.targets else "N/A"
    embed.add_field(name="Target", value=target)

    maxify = "\n".join([str(item) for item in factory.maximize]) if factory.maximize else "N/A"
    embed.add_field(name="Maximize", value=maxify)

    def group_recipes(names, limits={}):
        limits = {r.name: v for r, v in limits.items()}
        names = names | {n for n in limits.keys()}
        return sorted(list({n.split("#")[0] + (f" <= {rnd(limits.get(n))}" if n in limits else "") for n in names}))

    embed.add_field(name="Recipe Bank", value=factory.recipe_bank)
    embed.add_field(name="Recipe Includes", value="\n".join(group_recipes(factory.include_recipes)) if factory.include_recipes else "N/A")
    embed.add_field(name="Recipe Excludes", value="\n".join(group_recipes(factory.exclude_recipes, factory.limits)) if factory.exclude_recipes or factory.limits else "N/A")

    return embed


def solution_embed(solution: dict[ModifiedRecipe, float]) -> List[Embed]:
    def plrl(val: float) -> str:
        return "s" if val > 1 else ""

    consumption_map = build_consumption_map(solution)
    embeds: List[Embed] = [Embed()]
    for recipe, num in sorted(solution.items(), key=lambda kv: (kv[0].name, kv[0].sloops, kv[0].power_shards)):
        if len(embeds[-1].fields) >= MAX_FIELDS:
            embeds.append(Embed())

        name = recipe.original_recipe.name
        building = recipe.building.name

        if recipe.power_shards > 0:
            name = f"{name} @ {int(recipe.shard_scale * 100)}%"
            building = f"{building} with {recipe.power_shards} Power Shard{plrl(recipe.power_shards)}"

        if recipe.sloops > 0:
            name = f"{name} {'+' if ' @ ' in name else '@'} {recipe.sloop_scale}x"
            building = f"{building} {'+' if ' with ' in building else 'with'} {recipe.sloops} Somersloop{plrl(recipe.sloops)}"

        consumed_by = consumed_by_str(recipe.outputs, consumption_map, recipe.original_recipe.name)
        field_value = f"{rnd(num)} {building}\n{inout_str(recipe.inputs, recipe.outputs, num)}"
        if consumed_by:
            field_value = f"{field_value}\n{consumed_by}"
        embeds[-1].add_field(name=name, value=field_value, inline=False)

    summary = solution_summary(solution)
    footer = inout_str(summary.inputs, summary.outputs)
    if summary.total_shards > 0 or summary.total_sloops > 0:
        shards = f"{summary.total_shards} Power Shard{plrl(summary.total_shards)}"
        sloops = f"{summary.total_sloops} Somersloop{plrl(summary.total_sloops)}"
        joiner = " + " if summary.total_shards > 0 and summary.total_sloops > 0 else ""
        footer = f"{footer}\n{shards if summary.total_shards > 0 else ''}{joiner}{sloops if summary.total_sloops > 0 else ''}"
    embeds[-1].set_footer(text=footer)
    return embeds


def inout_str(inputs: Rates, outputs: Rates, scale_factor: float = 1.0) -> str:
    inputs = rates_str(inputs * scale_factor)
    output = rates_str(outputs * scale_factor)
    return f"{inputs} -> {output}"


def build_consumption_map(solution: dict[ModifiedRecipe, float]) -> dict[Item, list[tuple[str, float]]]:
    flat = [(item, recipe.original_recipe.name, rate * count) for recipe, count in solution.items() for item, rate in recipe.inputs.items()]
    items = set(item for item, _, _ in flat)
    return {item: [(name, amount) for i, name, amount in flat if i == item] for item in items}


def consumed_by_str(outputs: Rates, consumption_map: dict[Item, list[tuple[str, float]]], current_recipe: str) -> str:
    consumers = [(name, amount) for item in outputs for name, amount in consumption_map.get(item, []) if name != current_recipe]
    if not consumers:
        return ""
    names = set(name for name, _ in consumers)
    grouped = {name: sum(amount for n, amount in consumers if n == name) for name in names}
    parts = [f"{name}: {rnd(amount)}" for name, amount in sorted(grouped.items())]
    return "-# consumed by: " + ", ".join(parts)


@dataclass
class SolutionSummary:
    inputs: Rates
    outputs: Rates
    total_shards: int
    total_sloops: int


def solution_summary(solution: dict[ModifiedRecipe, float]) -> SolutionSummary:
    raw_creation = [r.name for r in raw()]
    inputs = reduce(sum_by_item, [r.inputs * -v for r, v in solution.items()], dict())
    outputs = reduce(sum_by_item, [r.outputs * v for r, v in solution.items() if r.original_recipe.name not in raw_creation], dict())
    totals = sum_by_item(inputs, outputs)
    return SolutionSummary(
        inputs=Rates(dict((k, -v) for k, v in totals.items() if v < 0)),
        outputs=Rates(dict((k, v) for k, v in totals.items() if v > 0)),
        total_shards=sum([ceil(n) * r.power_shards for r, n in solution.items()]),
        total_sloops=sum([ceil(n) * r.sloops for r, n in solution.items()]),
    )


def sum_by_item(lhs: Rates | dict[Item, float], rhs: Rates | dict[Item, float]) -> dict[Item, float]:
    sum = [(item, lhs.get(item, 0) + rhs.get(item, 0)) for item in Item if (item in lhs or item in rhs)]
    return dict((i, s) for i, s in sum if not isclose(s, 0, abs_tol=1e-4))
