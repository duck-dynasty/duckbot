from copy import copy
from unittest import mock

import pytest

from duckbot.cogs.games.satisfy import Satisfy
from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates
from duckbot.cogs.games.satisfy.recipe import all, as_slooped, default


@pytest.fixture
def clazz(bot) -> Satisfy:
    return Satisfy(bot)


@pytest.fixture
def default_factory(clazz, context) -> Factory:
    return clazz.factory(context)


async def test_reset_destroys_factory(clazz, context):
    empty_factory = Factory(Rates(), [], Rates(), set())
    clazz.save(context, empty_factory)
    await clazz.reset.callback(clazz, context)
    assert clazz.factory_cache == {}
    context.send.assert_called_once_with(f":factory: :fire: Factory for {context.author.display_name} cleared. Bitch. :fire: :factory:", delete_after=60)


async def test_factory_state_sends_something_i_guess(clazz, context):
    await clazz.factory_state.callback(clazz, context)
    context.send.assert_called_once()


async def test_add_input_stores_input_rate(clazz, context, default_factory):
    await clazz.add_input.callback(clazz, context, str(Item.IronOre), 30)
    default_factory.inputs = Item.IronOre * 30
    assert clazz.factory(context) == default_factory

    await clazz.add_input.callback(clazz, context, str(Item.IronIngot), 30)
    default_factory.inputs = Item.IronOre * 30 + Item.IronIngot * 30
    assert clazz.factory(context) == default_factory


async def test_add_target_stores_output_rate(clazz, context, default_factory):
    await clazz.add_target.callback(clazz, context, str(Item.IronOre), 30)
    default_factory.targets = Item.IronOre * 30
    assert clazz.factory(context) == default_factory

    await clazz.add_target.callback(clazz, context, str(Item.IronIngot), 30)
    default_factory.targets = Item.IronOre * 30 + Item.IronIngot * 30
    assert clazz.factory(context) == default_factory


async def test_add_maximize_stores_maximizer(clazz, context, default_factory):
    await clazz.add_maximize.callback(clazz, context, str(Item.IronOre))
    default_factory.maximize = {Item.IronOre}
    assert clazz.factory(context) == default_factory

    await clazz.add_maximize.callback(clazz, context, str(Item.IronIngot))
    default_factory.maximize = {Item.IronOre, Item.IronIngot}
    assert clazz.factory(context) == default_factory


async def test_add_booster_power_shard(clazz, context, default_factory):
    await clazz.add_booster.callback(clazz, context, str(Item.PowerShard), 10)
    default_factory.power_shards = 10
    assert clazz.factory(context) == default_factory


async def test_add_booster_sloops(clazz, context, default_factory):
    await clazz.add_booster.callback(clazz, context, str(Item.Somersloop), 10)
    default_factory.sloops = 10
    assert clazz.factory(context) == default_factory


async def test_recipe_bank_stores_bank(clazz, context):
    await clazz.recipe_bank.callback(clazz, context, "Default")
    assert clazz.factory(context).recipe_bank == "Default"


async def test_include_recipe_adds_include_no_boost(clazz, context):
    await clazz.include_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).include_recipes == {r.name for r in sloop([r for r in all() if r.name in ["IronOre"]])}

    await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).include_recipes == {r.name for r in sloop([r for r in all() if r.name in ["IronOre", "IronIngot"]])}


async def test_include_recipe_adds_include_with_boost(clazz, context):
    await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot), 3, 1)
    assert clazz.factory(context).include_recipes == {r.name for r in sloop(all()) if r.original_recipe.name == "IronIngot" and r.sloops == 1 and r.power_shards == 3}

    await clazz.include_recipe.callback(clazz, context, str(Item.CopperIngot), 2, 0)
    assert clazz.factory(context).include_recipes == {
        r.name
        for r in sloop(all())
        if (r.original_recipe.name == "IronIngot" and r.sloops == 1 and r.power_shards == 3) or (r.original_recipe.name == "CopperIngot" and r.sloops == 0 and r.power_shards == 2)
    }


async def test_include_recipe_removes_exclusion(clazz, context):
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronOre))
    await clazz.include_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).include_recipes == set()
    assert clazz.factory(context).exclude_recipes == set()


async def test_include_recipe_removes_boosted_exclusion(clazz, context):
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronIngot), 3, 1)
    await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).include_recipes == set()
    assert clazz.factory(context).exclude_recipes == set()


@pytest.mark.parametrize("shards,sloops", [(None, 0), (0, None)])
async def test_include_recipe_invalid_args(clazz, context, shards, sloops):
    with pytest.raises(ValueError):
        await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot), shards, sloops)


async def test_exclude_recipe_adds_exclude_no_boost(clazz, context):
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).exclude_recipes == {r.name for r in sloop([r for r in all() if r.name in ["IronOre"]])}

    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).exclude_recipes == {r.name for r in sloop([r for r in all() if r.name in ["IronOre", "IronIngot"]])}


async def test_exclude_recipe_removes_inclusion(clazz, context):
    await clazz.include_recipe.callback(clazz, context, str(Item.IronOre))
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronOre))
    assert clazz.factory(context).exclude_recipes == set()
    assert clazz.factory(context).include_recipes == set()


async def test_exclude_recipe_removes_boosted_inclusion(clazz, context):
    await clazz.include_recipe.callback(clazz, context, str(Item.IronIngot), 3, 1)
    await clazz.exclude_recipe.callback(clazz, context, str(Item.IronIngot))
    assert clazz.factory(context).exclude_recipes == set()
    assert clazz.factory(context).include_recipes == set()


@pytest.mark.parametrize("shards,sloops", [(None, 0), (0, None)])
async def test_exclude_recipe_invalid_args(clazz, context, shards, sloops):
    with pytest.raises(ValueError):
        await clazz.exclude_recipe.callback(clazz, context, str(Item.IronIngot), shards, sloops)


async def test_limit_recipe_adds_limit_no_boost(clazz, context, default_factory):
    await clazz.limit_recipe.callback(clazz, context, str(Item.IronOre), 30)
    assert clazz.factory(context).limits == {x: 30 for x in sloop([r for r in all() if r.name in ["IronOre"]])}

    await clazz.limit_recipe.callback(clazz, context, str(Item.IronIngot), 30)
    assert clazz.factory(context).limits == {x: 30 for x in sloop([r for r in all() if r.name in ["IronOre", "IronIngot"]])}


@pytest.mark.parametrize("shards,sloops", [(None, 0), (0, None)])
async def test_limit_recipe_invalid_args(clazz, context, shards, sloops):
    with pytest.raises(ValueError):
        await clazz.limit_recipe.callback(clazz, context, str(Item.IronIngot), 30, shards, sloops)


async def test_solve_no_factory_rejects(clazz, context):
    await clazz.solve.callback(clazz, context)
    context.send.assert_called_once_with("No.", delete_after=60)


async def test_solve_no_in_or_out(clazz, context, default_factory):
    await clazz.solve.callback(clazz, context)
    context.send.assert_called_once_with("No.", delete_after=60)


@mock.patch("duckbot.cogs.games.satisfy.satisfy.optimize", return_value=dict())
async def test_solve_all_defaults(opt, clazz, context, default_factory):
    default_factory.inputs = Item.IronOre * 30
    default_factory.maximize = {Item.IronOre}
    expected = copy(default_factory)
    expected.recipes = sloop(default())

    clazz.save(context, default_factory)
    await clazz.solve.callback(clazz, context)
    opt.assert_called_once_with(expected)


@mock.patch("duckbot.cogs.games.satisfy.satisfy.optimize", return_value=dict())
async def test_solve_different_recipe_bank(opt, clazz, context, default_factory):
    default_factory.inputs = Item.IronOre * 30
    default_factory.maximize = {Item.IronOre}
    default_factory.recipe_bank = "All"
    expected = copy(default_factory)
    expected.recipes = sloop(all())

    clazz.save(context, default_factory)
    await clazz.solve.callback(clazz, context)
    opt.assert_called_once_with(expected)


@mock.patch("duckbot.cogs.games.satisfy.satisfy.optimize", return_value=dict())
async def test_solve_recipe_includes(opt, clazz, context, default_factory):
    default_factory.inputs = Item.IronOre * 30
    default_factory.maximize = {Item.IronOre}
    default_factory.recipe_bank = "Default"
    default_factory.include_recipes = {x.name for r in all() for x in as_slooped(r) if r.name == "DilutedPackagedFuel"}
    expected = copy(default_factory)
    expected.recipes = sloop(default() + [r for r in all() if r.name == "DilutedPackagedFuel"])

    clazz.save(context, default_factory)
    await clazz.solve.callback(clazz, context)
    opt.assert_called_once_with(expected)


@mock.patch("duckbot.cogs.games.satisfy.satisfy.optimize", return_value=dict())
async def test_solve_recipe_excludes(opt, clazz, context, default_factory):
    default_factory.inputs = Item.IronOre * 30
    default_factory.maximize = {Item.IronOre}
    default_factory.exclude_recipes = {x.name for r in default() for x in as_slooped(r)} - {x.name for r in default() for x in as_slooped(r) if r.name == "IronIngot"}
    expected = copy(default_factory)
    expected.recipes = sloop([r for r in default() if r.name == "IronIngot"])

    clazz.save(context, default_factory)
    await clazz.solve.callback(clazz, context)
    opt.assert_called_once_with(expected)


def sloop(recipes):
    return {x for r in recipes for x in as_slooped(r)}
