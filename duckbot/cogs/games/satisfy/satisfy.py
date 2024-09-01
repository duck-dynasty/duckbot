from typing import List, Union

from discord import Interaction
from discord.app_commands import Choice, MissingPermissions, check
from discord.ext.commands import Cog, Context, hybrid_group

from .factory import Factory
from .item import Item
from .recipe import all
from .solver import optimize


async def allowed(context: Union[Context, Interaction]):
    id = context.author.id if hasattr(context, "author") else context.user.id
    if id not in [368038054558171141, 776607982472921088, 375024417358479380]:
        raise MissingPermissions(["lul"])
    return True


class Satisfy(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.factory_cache = {}

    def factory(self, context: Context) -> Factory:
        return self.factory_cache.get(context.author.id, Factory(inputs={}, targets={}, maximize=set(), recipes=all()))

    def save(self, context: Context, factory: Factory):
        self.factory_cache[context.author.id] = factory

    def clear(self, context: Context):
        self.factory_cache.pop(context.author.id, None)

    # things left to do
    #   clean up output; just dumping the Factory is ugly; final output is hard to read
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
        await context.send(f"Factory for {context.author.display_name} cleared. Bitch.", delete_after=10)

    @satisfy.command(name="input", description="Adds an input to the factory.")
    @check(allowed)
    async def add_input(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.inputs = factory.inputs | dict([Item[item] * rate_per_minute])
        self.save(context, factory)
        await context.send(f"Added {item} to inputs. Current factory={factory}", delete_after=10)

    @satisfy.command(name="output", description="Specifies a desired output for the factory.")
    @check(allowed)
    async def add_target(self, context: Context, item: str, rate_per_minute: float):
        factory = self.factory(context)
        factory.targets = factory.targets | dict([Item[item] * rate_per_minute])
        self.save(context, factory)
        await context.send(f"Added {item} to output targets. Current factory={factory}", delete_after=10)

    @satisfy.command(name="maximize", description="Specify maximize output of desired item.")
    @check(allowed)
    async def add_maximize(self, context: Context, item: str):
        factory = self.factory(context)
        factory.maximize.add(Item[item])
        self.save(context, factory)
        await context.send(f"Added {item} to maximization targets. Current factory={factory}", delete_after=10)

    @satisfy.command(name="solve", description="Runs the solver for the factory.")
    @check(allowed)
    async def solve(self, context: Context):
        async with context.typing():
            result = optimize(self.factory(context))
            await context.send(str(result))

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
