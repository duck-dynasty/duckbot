from typing import List

from discord import Interaction
from discord.app_commands import Choice, MissingPermissions, check
from discord.ext.commands import Cog, Context, hybrid_group

from .factory import Factory
from .item import Item
from .pretty import factory_embed, solution_embed
from .rate import Rates
from .recipe import all
from .solver import optimize


async def allowed(context: Context | Interaction):
    id = context.author.id if hasattr(context, "author") else context.user.id
    if id not in [368038054558171141, 776607982472921088, 375024417358479380]:
        raise MissingPermissions(["lul"])
    return True


class Satisfy(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.factory_cache = {}

    def factory(self, context: Context) -> Factory:
        return self.factory_cache.get(context.author.id, Factory(inputs=Rates(), targets=Rates(), maximize=set(), recipes=all()))
        # return self.factory_cache.get(context.author.id, Factory(inputs=Item.CrudeOil * 300 + Item.Water * 1000, targets=Rates(), maximize=set([Item.Plastic]), recipes=all()))

    def save(self, context: Context, factory: Factory):
        self.factory_cache[context.author.id] = factory

    def clear(self, context: Context):
        self.factory_cache.pop(context.author.id, None)

    # things left to do
    #   add the rest of the recipes/items
    #   create `recipe_bank`, `include_recipe`, `exclude_recipe` commands for recipe manipulation
    #   ensure solve is feasible; add raw item resource creation
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

    @satisfy.command(name="solve", description="Runs the solver for the factory.")
    @check(allowed)
    async def solve(self, context: Context):
        factory = self.factory(context)
        if not factory.inputs or (not factory.targets and not factory.maximize):
            await context.send("No.", delete_after=10)
        else:
            async with context.typing():
                solution = optimize(factory)
                await context.send(embeds=[factory_embed(factory), solution_embed(solution)])

    @add_input.autocomplete("item")
    @add_target.autocomplete("item")
    @add_maximize.autocomplete("item")
    async def items(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        if len(current) < 3:
            return []
        else:
            items = [i.name for i in Item]
            return [Choice(name=i, value=i) for i in items if current.lower() in i.lower()]

    @reset.error
    @add_input.error
    @add_target.error
    @add_maximize.error
    async def on_error(self, context: Context, error):
        await context.send(str(error), delete_after=10)
