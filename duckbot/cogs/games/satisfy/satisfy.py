from typing import List

from discord import Interaction
from discord.app_commands import Choice, MissingPermissions, check
from discord.ext.commands import Cog, Context, hybrid_group

from .factory import Factory
from .item import Item
from .pretty import factory_embed, solution_embed
from .rate import Rates
from .recipe import all, default
from .solver import optimize


async def allowed(context: Context | Interaction):
    id = context.author.id if hasattr(context, "author") else context.user.id
    if id not in [368038054558171141, 776607982472921088, 375024417358479380]:
        raise MissingPermissions(["lul"])
    return True


recipe_banks = {
    "All": all(),
    "Default": default(),
}


class Satisfy(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.factory_cache = {}
        self.item_names = [i.name for i in Item]
        self.recipe_names = [r.name for r in all()]

    def factory(self, context: Context) -> Factory:
        factory = Factory(inputs=Rates(), targets=Rates(), maximize=set(), recipes=all())
        # factory = Factory(inputs=Item.CrudeOil * 300 + Item.Water * 1000, targets=Rates(), maximize=set([Item.Plastic]), recipes=all())
        # monkeypatch fields for recipe manipulations
        factory.recipe_bank = "All"
        factory.include_recipes = set()
        factory.exclude_recipes = set()
        return self.factory_cache.get(context.author.id, factory)

    def save(self, context: Context, factory: Factory):
        self.factory_cache[context.author.id] = factory

    def clear(self, context: Context):
        self.factory_cache.pop(context.author.id, None)

    # things left to do
    #   add the rest of the recipes/items
    #   make solve prefer to not leave non-sinkable items
    #   ensure solve is feasible; add raw item resource creation?
    #   save factories by name per user, instead of 1 factory per user?
    #   and like, tests, I guess

    @hybrid_group(name="satisfy", description="Satisfy yourself")
    async def satisfy(self, context: Context):
        pass

    @satisfy.command(name="reset", description="Clears factory inputs built so far.")
    @check(allowed)
    async def reset(self, context: Context):
        self.clear(context)
        await context.send(f":factory: :fire: Factory for {context.author.display_name} cleared. Bitch. :fire: :factory:", delete_after=10)

    @satisfy.command(name="input", description="Adds an input to the factory.")
    @check(allowed)
    async def add_input(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.inputs = factory.inputs + Item[item] * rate_per_minute
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @satisfy.command(name="output", description="Specifies a desired output for the factory.")
    @check(allowed)
    async def add_target(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.targets = factory.targets + Item[item] * rate_per_minute
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @satisfy.command(name="maximize", description="Specify maximize output of desired item.")
    @check(allowed)
    async def add_maximize(self, context: Context, item: str):
        factory = self.factory(context)
        factory.maximize.add(Item[item])
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @satisfy.group(name="recipe", description="Recipe related manipulations.")
    async def recipe(self, context: Context):
        pass

    @recipe.command(name="bank", description="Select a recipe bank for the factory to use. Default is All.")
    async def recipe_bank(self, context: Context, recipe_bank: str):
        factory = self.factory(context)
        factory.recipe_bank = recipe_bank
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @recipe.command(name="include", description="Forces a recipe to be available to the solver. Overrides `exclude`")
    async def include_recipe(self, context: Context, recipe: str):
        factory = self.factory(context)
        factory.include_recipes.add(recipe)
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @recipe.command(name="exclude", description="Makes a recipe to be unavailable to the solver. Overridden by `include`")
    async def exclude_recipe(self, context: Context, recipe: str):
        factory = self.factory(context)
        factory.exclude_recipes.add(recipe)
        self.save(context, factory)
        await context.send(embed=factory_embed(factory), delete_after=10)

    @satisfy.command(name="solve", description="Runs the solver for the factory.")
    @check(allowed)
    async def solve(self, context: Context):
        factory = self.factory(context)
        if not factory.inputs or (not factory.targets and not factory.maximize):
            await context.send("No.", delete_after=10)
        else:
            async with context.typing():
                recipes = [r for r in recipe_banks[factory.recipe_bank] if r.name not in factory.exclude_recipes]
                names = [r.name for r in recipes]
                factory.recipes = recipes + [r for r in all() if r.name in factory.include_recipes and r.name not in names]
                solution = optimize(factory)
                await context.send(embeds=[factory_embed(factory), solution_embed(solution)])

    @add_input.autocomplete("item")
    @add_target.autocomplete("item")
    @add_maximize.autocomplete("item")
    async def items(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(self.item_names, current)

    @recipe_bank.autocomplete("recipe_bank")
    async def recipe_banks(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(recipe_banks.keys(), current)

    @include_recipe.autocomplete("recipe")
    @exclude_recipe.autocomplete("recipe")
    async def recipes(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(self.recipe_names, current)

    @reset.error
    @add_input.error
    @add_target.error
    @add_maximize.error
    @recipe_bank.error
    @include_recipe.error
    @exclude_recipe.error
    @solve.error
    async def on_error(self, context: Context, error):
        await context.send(str(error), delete_after=10)


def choices(list: List[str], needle: str) -> List[Choice[str]]:
    if len(needle) < 3:
        return []
    else:
        return [Choice(name=i, value=i) for i in list if needle.lower() in i.lower()]
