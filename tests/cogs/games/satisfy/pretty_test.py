from unittest import mock

from discord import Embed

from duckbot.cogs.games.satisfy.factory import Factory
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.pretty import factory_embed, solution_embed
from duckbot.cogs.games.satisfy.recipe import ModifiedRecipe, all


def recipe_by_name(name: str, power_shards: int = 0, sloops: int = 0) -> ModifiedRecipe:
    return ModifiedRecipe(next(r for r in all() if r.name == name), power_shards, sloops)


def test_solution_embed_renders_consumed_by_for_chained_recipes():
    ingot = recipe_by_name("IronIngot")
    plate = recipe_by_name("IronPlate")
    result = solution_embed({ingot: 1.0, plate: 1.0})

    expected = Embed()
    expected.add_field(name="IronIngot", value="1.0 Smelter\n30.0 IronOre -> 30.0 IronIngot\n-# consumed by: IronPlate: 30.0", inline=False)
    expected.add_field(name="IronPlate", value="1.0 Constructor\n30.0 IronIngot -> 20.0 IronPlate", inline=False)
    expected.set_footer(text="30.0 IronOre -> 20.0 IronPlate")
    assert result == [expected]


# MAX_FIELDS shrunk to 1 so two recipes suffice; otherwise this test would need 26+ hand-written field literals.
@mock.patch("duckbot.cogs.games.satisfy.pretty.MAX_FIELDS", 1)
def test_solution_embed_splits_into_multiple_embeds_when_exceeding_max_fields():
    ingot = recipe_by_name("IronIngot")
    plate = recipe_by_name("IronPlate")
    result = solution_embed({ingot: 1.0, plate: 1.0})

    first = Embed()
    first.add_field(name="IronIngot", value="1.0 Smelter\n30.0 IronOre -> 30.0 IronIngot\n-# consumed by: IronPlate: 30.0", inline=False)
    second = Embed()
    second.add_field(name="IronPlate", value="1.0 Constructor\n30.0 IronIngot -> 20.0 IronPlate", inline=False)
    second.set_footer(text="30.0 IronOre -> 20.0 IronPlate")
    assert result == [first, second]


def maximize_field(factory: Factory) -> str:
    factory.recipe_bank = "Default"
    factory.include_recipes = set()
    factory.exclude_recipes = set()
    return next(f.value for f in factory_embed(factory).fields if f.name == "Maximize")


def test_factory_embed_no_maximize():
    assert maximize_field(Factory()) == "N/A"


def test_factory_embed_lists_maximize_in_priority_order():
    assert maximize_field(Factory(maximize=[Item.IronPlate, Item.Computer])) == "1. IronPlate\n2. Computer"
