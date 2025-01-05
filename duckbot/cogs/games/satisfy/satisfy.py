from typing import List, Optional

from discord import Interaction
from discord.app_commands import Choice
from discord.ext.commands import Cog, Context, hybrid_group

from duckbot.util.embeds import group_by_max_length

from .factory import Factory
from .item import Item
from .pretty import factory_embed, solution_embed
from .recipe import all, as_slooped
from .recipe_banks import recipe_banks
from .solver import optimize

item_names = [i.name for i in Item]
boost_item_names = [Item.PowerShard.name, Item.Somersloop.name]
recipes_by_name = {r.name: r for r in all()}


class Satisfy(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.factory_cache = {}

    def factory(self, context: Context) -> Factory:
        factory = Factory()
        # monkeypatch fields for recipe manipulations
        factory.recipe_bank = "Default"
        factory.include_recipes = set()
        factory.exclude_recipes = set()
        return self.factory_cache.get(context.author.id, factory)

    def save(self, context: Context, factory: Factory):
        self.factory_cache[context.author.id] = factory

    def clear(self, context: Context):
        self.factory_cache.pop(context.author.id, None)

    @hybrid_group(name="satisfy", description="Satisfy yourself")
    async def satisfy(self, context: Context):
        pass

    @satisfy.command(name="reset", description="Clears factory inputs built so far.")
    async def reset(self, context: Context):
        self.clear(context)
        await context.send(f":factory: :fire: Factory for {context.author.display_name} cleared. Bitch. :fire: :factory:", delete_after=60)

    @satisfy.command(name="state", description="Displays the current factory.")
    async def factory_state(self, context: Context):
        await context.send(embed=factory_embed(self.factory(context)), delete_after=1800)

    @satisfy.command(name="input", description="Adds an input to the factory.")
    async def add_input(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.inputs = factory.inputs + Item[item] * rate_per_minute
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @satisfy.command(name="output", description="Specifies a desired output for the factory.")
    async def add_target(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.targets = factory.targets + Item[item] * rate_per_minute
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @satisfy.command(name="maximize", description="Specify maximize output of desired item.")
    async def add_maximize(self, context: Context, item: str):
        factory = self.factory(context)
        factory.maximize.add(Item[item])
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @satisfy.command(name="booster", description="Specify how many of a booster item is available to use.")
    async def add_booster(self, context: Context, boost_item: str, amount: int):
        factory = self.factory(context)
        item = Item[boost_item]
        if item == Item.PowerShard:
            factory.power_shards = amount
        elif item == Item.Somersloop:
            factory.sloops = amount
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @satisfy.group(name="recipe", description="Recipe related manipulations.")
    async def recipe(self, context: Context):
        pass

    @recipe.command(name="bank", description="Select a recipe bank for the factory to use. Default is... Default.")
    async def recipe_bank(self, context: Context, recipe_bank: str):
        factory = self.factory(context)
        factory.recipe_bank = recipe_bank
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @recipe.command(name="include", description="Forces a recipe to be available to the solver. Undoes /satisfy recipe exclude")
    async def include_recipe(self, context: Context, recipe: str, power_shards: Optional[int] = None, sloops: Optional[int] = None):
        if (power_shards is not None and sloops is None) or (power_shards is None and sloops is not None):
            raise ValueError("Both power shards and sloops must be specified, or neither.")
        factory = self.factory(context)
        to_include = [r.name for r in recipes_matching(recipe, power_shards, sloops)]
        if any(i in factory.exclude_recipes for i in to_include):
            factory.exclude_recipes = factory.exclude_recipes - set(to_include)
        else:
            factory.include_recipes = factory.include_recipes | set(to_include)
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @recipe.command(name="exclude", description="Makes a recipe to be unavailable to the solver. Undoes /satisfy recipe include")
    async def exclude_recipe(self, context: Context, recipe: str, power_shards: Optional[int] = None, sloops: Optional[int] = None):
        if (power_shards is not None and sloops is None) or (power_shards is None and sloops is not None):
            raise ValueError("Both power shards and sloops must be specified, or neither.")
        factory = self.factory(context)
        to_exclude = [r.name for r in recipes_matching(recipe, power_shards, sloops)]
        if any(i in factory.include_recipes for i in to_exclude):
            factory.include_recipes = factory.include_recipes - set(to_exclude)
        else:
            factory.exclude_recipes = factory.exclude_recipes | set(to_exclude)
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @recipe.command(name="limit", description="Limits the number of times a recipe can be used.")
    async def limit_recipe(self, context: Context, recipe: str, limit: float, power_shards: Optional[int] = None, sloops: Optional[int] = None):
        if (power_shards is not None and sloops is None) or (power_shards is None and sloops is not None):
            raise ValueError("Both power shards and sloops must be specified, or neither.")
        factory = self.factory(context)
        for r in recipes_matching(recipe, power_shards, sloops):
            factory.limits[r] = limit
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=60)

    @satisfy.command(name="solve", description="Runs the solver for the factory.")
    async def solve(self, context: Context):
        factory = self.factory(context)
        if factory.targets or (factory.inputs and factory.maximize):
            async with context.typing():
                bank = [x for r in recipe_banks[factory.recipe_bank] for x in as_slooped(r)]
                recipes = [r for r in bank if r.name not in factory.exclude_recipes]
                includes = [x for r in all() for x in as_slooped(r) if x.name in factory.include_recipes]
                factory.recipes = {r for r in (recipes + includes)}
                solution = optimize(factory)
                if solution is None:
                    await context.send("Why do you hate possible?", delete_after=60)
                else:
                    for embeds in group_by_max_length([factory_embed(factory)] + solution_embed(solution)):
                        await context.send(embeds=embeds)
        else:
            await context.send("No.", delete_after=60)

    @add_input.autocomplete("item")
    @add_target.autocomplete("item")
    @add_maximize.autocomplete("item")
    async def items(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(item_names, current)

    @add_booster.autocomplete("boost_item")
    async def boost_items(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(boost_item_names, current, threshold=0)

    @recipe_bank.autocomplete("recipe_bank")
    async def recipe_banks(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(recipe_banks.keys(), current, threshold=0)

    @include_recipe.autocomplete("recipe")
    @exclude_recipe.autocomplete("recipe")
    @limit_recipe.autocomplete("recipe")
    async def recipes(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(recipes_by_name.keys(), current)

    @include_recipe.autocomplete("power_shards")
    @exclude_recipe.autocomplete("power_shards")
    @limit_recipe.autocomplete("power_shards")
    async def power_shards(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        r = recipes_by_name[interaction.namespace.recipe]
        return [Choice(name=str(p), value=str(p)) for p in range(r.building.max_shards + 1)]

    @include_recipe.autocomplete("sloops")
    @exclude_recipe.autocomplete("sloops")
    @limit_recipe.autocomplete("sloops")
    async def sloops(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        r = recipes_by_name[interaction.namespace.recipe]
        return [Choice(name=str(s), value=str(s)) for s in range(r.building.max_sloop + 1)]

    @reset.error
    @add_input.error
    @add_target.error
    @add_maximize.error
    @add_booster.error
    @recipe_bank.error
    @include_recipe.error
    @exclude_recipe.error
    @limit_recipe.error
    @solve.error
    async def on_error(self, context: Context, error):
        await context.send(str(error), delete_after=60)


def recipes_matching(recipe_name: str, power_shards: Optional[int], sloops: Optional[int]) -> List[str]:
    r = recipes_by_name[recipe_name]
    slooped = as_slooped(r)
    return slooped if power_shards is None and sloops is None else [r for r in slooped if r.power_shards == power_shards and r.sloops == sloops]


def choices(pool: List[str], needle: str, threshold: int = 3) -> List[Choice[str]]:
    def match(needle: str, haystack: str) -> bool:
        import builtins

        it = iter(haystack)
        return builtins.all(any(next_letter == ch for next_letter in it) for ch in needle)

    if len(needle) < threshold:
        return []
    else:
        return [Choice(name=i, value=i) for i in pool if match(needle.lower(), i.lower())][:25]
