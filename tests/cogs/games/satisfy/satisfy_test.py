import pytest

from duckbot.cogs.games.satisfy import Satisfy
from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rate import Rates
from duckbot.cogs.games.satisfy.recipe import all


@pytest.fixture
def clazz(bot) -> Satisfy:
    return Satisfy(bot)


@pytest.fixture
def empty_factory() -> Factory:
    return Factory(Rates(), [], Rates(), set())


@pytest.fixture
def default_factory() -> Factory:
    return Factory(Rates(), all(), Rates(), set())


async def test_reset_destroys_factory(clazz, context, empty_factory):
    clazz.save(context, empty_factory)
    await clazz.reset.callback(clazz, context)
    assert clazz.factory_cache == {}
    context.send.assert_called_once_with(f":factory: :fire: Factory for {context.author.display_name} cleared. Bitch. :fire: :factory:", delete_after=10)


async def test_add_input_stores_input_rate(clazz, context, default_factory):
    await clazz.add_input.callback(clazz, context, str(Item.IronOre), 30)
    default_factory.inputs = Rates([Item.IronOre * 30])
    assert clazz.factory(context) == default_factory

    await clazz.add_input.callback(clazz, context, str(Item.IronIngot), 30)
    default_factory.inputs = Item.IronOre * 30 + Item.IronIngot * 30
    assert clazz.factory(context) == default_factory


async def test_add_target_stores_output_rate(clazz, context, default_factory):
    await clazz.add_target.callback(clazz, context, str(Item.IronOre), 30)
    default_factory.targets = Rates([Item.IronOre * 30])
    assert clazz.factory(context) == default_factory

    await clazz.add_target.callback(clazz, context, str(Item.IronIngot), 30)
    default_factory.targets = Item.IronOre * 30 + Item.IronIngot * 30
    assert clazz.factory(context) == default_factory


async def test_add_maximize_stores_maximizer(clazz, context, default_factory):
    await clazz.add_maximize.callback(clazz, context, str(Item.IronOre))
    default_factory.maximize = set([Item.IronOre])
    assert clazz.factory(context) == default_factory

    await clazz.add_maximize.callback(clazz, context, str(Item.IronIngot))
    default_factory.maximize = set([Item.IronOre, Item.IronIngot])
    assert clazz.factory(context) == default_factory


async def test_recipe_bank_stores_bank(clazz, context):
    await clazz.recipe_bank.callback(clazz, context, "Default")
    assert clazz.factory(context).recipe_bank == "Default"


async def test_include_recipe_adds_include(clazz, context):
    await clazz.include_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).include_recipes == set(["IronOre"])

    await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).include_recipes == set(["IronOre", "IronIngot"])


async def test_exclude_recipe_adds_include(clazz, context):
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).exclude_recipes == set(["IronOre"])

    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).exclude_recipes == set(["IronOre", "IronIngot"])


async def test_solve_no_factory_rejects(clazz, context):
    await clazz.solve.callback(clazz, context)
    context.send.assert_called_once_with("No.", delete_after=10)


async def test_solve_no_target_or_max_rejects(clazz, context, default_factory):
    clazz.save(context, default_factory)
    await clazz.solve.callback(clazz, context)
    context.send.assert_called_once_with("No.", delete_after=10)
