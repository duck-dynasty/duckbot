import io

from duckbot.cogs.games.satisfy.graph import solution_graph
from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.recipe import ModifiedRecipe, all


def recipe_by_name(name, power_shards=0, sloops=0):
    return ModifiedRecipe(next(r for r in all() if r.name == str(name)), power_shards, sloops)


def test_solution_graph_empty_returns_png():
    result = solution_graph({})
    assert isinstance(result, io.BytesIO)
    assert result.read(4) == b"\x89PNG"


def test_solution_graph_single_recipe_returns_png():
    result = solution_graph({recipe_by_name(Item.IronIngot): 1.0})
    assert isinstance(result, io.BytesIO)
    assert result.read(4) == b"\x89PNG"


def test_solution_graph_chain_returns_png():
    solution = {
        recipe_by_name(Item.IronOre): 0.5,
        recipe_by_name(Item.IronIngot): 1.0,
        recipe_by_name(Item.IronPlate): 1.0,
    }
    result = solution_graph(solution)
    assert isinstance(result, io.BytesIO)
    assert result.read(4) == b"\x89PNG"


def test_solution_graph_seek_position_is_zero():
    result = solution_graph({recipe_by_name(Item.IronIngot): 1.0})
    assert result.tell() == 0
