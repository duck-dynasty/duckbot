import io

import graphviz

from .item import Item
from .pretty import build_consumption_map, rnd
from .recipe import ModifiedRecipe, raw

_BG_COLOR = "#1e1e2e"
_NODE_FILL = "#2a2a3d"
_TEXT_COLOR = "#ffffff"
_EDGE_LABEL_COLOR = "#c3c2b7"
_INPUT_COLOR = "#199e70"
_RECIPE_COLOR = "#3987e5"
_OUTPUT_COLOR = "#c98500"

_GRAPH_ATTR = {"rankdir": "LR", "bgcolor": _BG_COLOR, "splines": "polyline", "nodesep": "0.3", "ranksep": "0.6", "pad": "0.4", "dpi": "150"}
_NODE_ATTR = {"shape": "box", "style": "rounded,filled", "fillcolor": _NODE_FILL, "fontcolor": _TEXT_COLOR, "fontname": "Helvetica bold", "fontsize": "12", "penwidth": "2", "margin": "0.2,0.1"}
_EDGE_ATTR = {"fontname": "Helvetica", "fontsize": "10", "fontcolor": _EDGE_LABEL_COLOR, "penwidth": "1.5", "arrowsize": "0.7"}

_RAW_RECIPE_NAMES = {r.name for r in raw()}


def solution_graph(solution: dict[ModifiedRecipe, float]) -> io.BytesIO:
    graph = _build_graph(solution) if solution else _empty_graph()
    return io.BytesIO(graph.pipe(format="png"))


def _empty_graph() -> graphviz.Digraph:
    graph = graphviz.Digraph(graph_attr={"bgcolor": _BG_COLOR, "pad": "0.5"})
    graph.node("empty", label="No solution", shape="plaintext", fontcolor=_TEXT_COLOR, fontname="Helvetica bold")
    return graph


def _build_graph(solution: dict[ModifiedRecipe, float]) -> graphviz.Digraph:
    produced_items: set[Item] = {item for recipe in solution for item in recipe.outputs}
    consumed_items: set[Item] = {item for recipe in solution for item in recipe.inputs}
    input_items = consumed_items - produced_items
    output_items = produced_items - consumed_items

    graph = graphviz.Digraph(graph_attr=_GRAPH_ATTR, node_attr=_NODE_ATTR, edge_attr=_EDGE_ATTR)
    for item in input_items:
        graph.node(_item_id(item), label=str(item), color=_INPUT_COLOR)
    for recipe, count in solution.items():
        graph.node(_recipe_id(recipe), label=f"{recipe.original_recipe.name}\\n{recipe.building.name} ×{rnd(count)}", color=_recipe_color(recipe))
    for item in output_items:
        graph.node(_item_id(item), label=str(item), color=_OUTPUT_COLOR)

    for (source, dest, color), labels in _build_edges(solution, input_items, output_items).items():
        graph.edge(source, dest, label="\\n".join(labels), color=color)
    return graph


def _build_edges(solution: dict[ModifiedRecipe, float], input_items: set[Item], output_items: set[Item]) -> dict[tuple[str, str, str], list[str]]:
    consumption_map = build_consumption_map(solution)
    edges: dict[tuple[str, str, str], list[str]] = {}
    for recipe, count in solution.items():
        for item in recipe.inputs:
            if item in input_items:
                edges.setdefault((_item_id(item), _recipe_id(recipe), _INPUT_COLOR), []).append(f"{rnd(recipe.inputs.get(item, 0) * count)}/min")
        for item in recipe.outputs:
            consumer_rates = {name: rate for name, rate in consumption_map.get(item, []) if name != recipe.original_recipe.name}
            for other in solution:
                if other.original_recipe.name in consumer_rates:
                    edges.setdefault((_recipe_id(recipe), _recipe_id(other), _recipe_color(recipe)), []).append(f"{rnd(consumer_rates[other.original_recipe.name])}/min")
            if not consumer_rates and item in output_items:
                edges.setdefault((_recipe_id(recipe), _item_id(item), _OUTPUT_COLOR), []).append(f"{rnd(recipe.outputs.get(item, 0) * count)}/min")
    return edges


def _recipe_color(recipe: ModifiedRecipe) -> str:
    return _INPUT_COLOR if recipe.original_recipe.name in _RAW_RECIPE_NAMES else _RECIPE_COLOR


# ":" would be parsed as graphviz port syntax in edge endpoints
def _item_id(item: Item) -> str:
    return f"item_{item.name}"


def _recipe_id(recipe: ModifiedRecipe) -> str:
    return f"recipe_{recipe.name}"
