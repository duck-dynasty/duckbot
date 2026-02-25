import colorsys
import io
from collections import Counter, deque

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.collections import LineCollection

from .item import Item
from .pretty import build_consumption_map, rnd
from .recipe import ModifiedRecipe

_GOLDEN_RATIO = (1 + 5**0.5) / 2
_BG_COLOR = "#1e1e2e"


def solution_graph(solution: dict[ModifiedRecipe, float]) -> io.BytesIO:
    if not solution:
        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor(_BG_COLOR)
        ax.set_facecolor(_BG_COLOR)
        ax.text(0.5, 0.5, "No solution", ha="center", va="center", transform=ax.transAxes, color="white")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=_BG_COLOR)
        plt.close(fig)
        buf.seek(0)
        return buf

    graph = _build_graph(solution)
    layer = {n: graph.nodes[n]["layer"] for n in graph.nodes}
    max_layer = max(layer.values(), default=0)

    ordering = _barycenter_order(graph, layer, max_layer)
    pos = _layered_positions(ordering, max_layer)

    node_colors_map = {n: colorsys.hsv_to_rgb(i / _GOLDEN_RATIO % 1, 0.65, 0.9) for i, n in enumerate(graph.nodes)}
    node_colors = [node_colors_map[n] for n in graph.nodes]
    labels = {n: graph.nodes[n]["label"] for n in graph.nodes}

    nodes_per_layer = Counter(layer.values())
    max_in_layer = max(nodes_per_layer.values(), default=1)
    fig, ax = plt.subplots(figsize=(max(12, (max_layer + 1) * 3), max(8, max_in_layer * 1.5)))
    fig.patch.set_facecolor(_BG_COLOR)
    ax.set_facecolor(_BG_COLOR)

    # Draw edges first so nodes render on top, hiding line endpoints inside circles
    _draw_gradient_edges(ax, graph, pos, node_colors_map)
    node_collection = nx.draw_networkx_nodes(graph, pos, ax=ax, node_color=node_colors, node_size=1500, alpha=1.0)
    node_collection.set_zorder(3)
    label_artists = nx.draw_networkx_labels(graph, pos, labels=labels, ax=ax, font_size=7, font_weight="bold", font_color="white")
    for text in label_artists.values():
        text.set_zorder(4)
    _draw_edge_labels(ax, graph, pos, node_colors_map)

    ax.axis("off")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120, facecolor=_BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    return buf


def _build_graph(solution: dict[ModifiedRecipe, float]) -> nx.DiGraph:
    graph = nx.DiGraph()
    consumption_map = build_consumption_map(solution)

    produced_items: set[Item] = {item for recipe in solution for item in recipe.outputs}
    consumed_items: set[Item] = {item for recipe in solution for item in recipe.inputs}
    input_items = consumed_items - produced_items
    output_items = produced_items - consumed_items

    for item in input_items:
        graph.add_node(_item_id(item), label=str(item))
    for recipe, count in solution.items():
        graph.add_node(_recipe_id(recipe), label=f"{recipe.original_recipe.name}\n\u00d7{rnd(count)}")
    for item in output_items:
        graph.add_node(_item_id(item), label=str(item))

    for recipe, count in solution.items():
        for item in recipe.inputs:
            if item in input_items:
                graph.add_edge(_item_id(item), _recipe_id(recipe), label=f"{rnd(recipe.inputs.get(item, 0) * count)}/min")
        _add_recipe_output_edges(graph, recipe, count, solution, output_items, consumption_map)

    _assign_layers(graph)
    return graph


def _add_recipe_output_edges(graph: nx.DiGraph, recipe: ModifiedRecipe, count: float, solution: dict, output_items: set, consumption_map: dict) -> None:
    for item in recipe.outputs:
        consumer_rates = {name: rate for name, rate in consumption_map.get(item, []) if name != recipe.original_recipe.name}
        if consumer_rates:
            for consumer_name, rate in consumer_rates.items():
                for other_recipe in solution:
                    if other_recipe.original_recipe.name == consumer_name:
                        edge_key = (_recipe_id(recipe), _recipe_id(other_recipe))
                        if graph.has_edge(*edge_key):
                            graph.edges[edge_key]["label"] = graph.edges[edge_key].get("label", "") + f"\n{rnd(rate)}/min"
                        else:
                            graph.add_edge(_recipe_id(recipe), _recipe_id(other_recipe), label=f"{rnd(rate)}/min")
        elif item in output_items:
            graph.add_edge(_recipe_id(recipe), _item_id(item), label=f"{rnd(recipe.outputs.get(item, 0) * count)}/min")


def _item_id(item: Item) -> str:
    return f"item:{item.name}"


def _recipe_id(recipe: ModifiedRecipe) -> str:
    return f"recipe:{recipe.name}"


def _assign_layers(graph: nx.DiGraph) -> None:
    layer: dict[str, int] = {n: 0 for n in graph.nodes if graph.in_degree(n) == 0}
    queue = deque(layer.keys())
    while queue:
        node = queue.popleft()
        for successor in graph.successors(node):
            new_depth = layer[node] + 1
            if successor not in layer or layer[successor] < new_depth:
                layer[successor] = new_depth
                queue.append(successor)
    for node in graph.nodes:
        graph.nodes[node]["layer"] = layer.get(node, 0)


def _barycenter_order(graph: nx.DiGraph, layer: dict, max_layer: int) -> dict[int, list]:
    ordering: dict[int, list] = {}
    for n, lyr in layer.items():
        ordering.setdefault(lyr, []).append(n)

    pos = {n: i for nodes in ordering.values() for i, n in enumerate(nodes)}
    for _ in range(20):
        for lyr in range(1, max_layer + 1):
            ordering[lyr].sort(key=lambda n: _bary(pos, list(graph.predecessors(n))))
            for i, n in enumerate(ordering[lyr]):
                pos[n] = i
        for lyr in range(max_layer - 1, -1, -1):
            ordering[lyr].sort(key=lambda n: _bary(pos, list(graph.successors(n))))
            for i, n in enumerate(ordering[lyr]):
                pos[n] = i

    _adjacent_swap(ordering, graph, pos)
    return ordering


def _adjacent_swap(ordering: dict[int, list], graph: nx.DiGraph, pos: dict) -> None:
    for _ in range(10):
        for nodes in ordering.values():
            for i in range(len(nodes) - 1):
                a, b = nodes[i], nodes[i + 1]
                a_nb = [n for n in list(graph.predecessors(a)) + list(graph.successors(a)) if n in pos]
                b_nb = [n for n in list(graph.predecessors(b)) + list(graph.successors(b)) if n in pos]
                cross_ab = sum(1 for na in a_nb for nb in b_nb if pos[na] > pos[nb])
                cross_ba = sum(1 for na in a_nb for nb in b_nb if pos[na] < pos[nb])
                if cross_ba < cross_ab:
                    nodes[i], nodes[i + 1] = b, a
                    pos[a], pos[b] = i + 1, i


def _bary(pos: dict, neighbors: list) -> float:
    return sum(pos.get(nb, 0) for nb in neighbors) / len(neighbors) if neighbors else 0.0


def _layered_positions(ordering: dict[int, list], max_layer: int) -> dict:
    pos = {}
    for lyr, nodes in ordering.items():
        n = len(nodes)
        x = lyr / max_layer if max_layer > 0 else 0.5
        for i, node in enumerate(nodes):
            y = 1.0 - (i / (n - 1) if n > 1 else 0.5)
            pos[node] = (x, y)
    return pos


def _bez(x0, y0, cx, cy, x1, y1, t):
    return ((1 - t) ** 2 * x0 + 2 * t * (1 - t) * cx + t**2 * x1, (1 - t) ** 2 * y0 + 2 * t * (1 - t) * cy + t**2 * y1)


def _arc_control(x0, y0, x1, y1, rad=0.1):
    dx, dy = x1 - x0, y1 - y0
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return mx - rad * dy, my + rad * dx


def _draw_gradient_edges(ax, graph: nx.DiGraph, pos: dict, node_colors_map: dict, rad: float = 0.1, n_segments: int = 25) -> None:
    for u, v in graph.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        if np.hypot(x1 - x0, y1 - y0) < 1e-10:
            continue

        cx, cy = _arc_control(x0, y0, x1, y1, rad)
        # Full center-to-center line; nodes are drawn on top (zorder=3) to hide endpoints inside circles
        t_vals = np.linspace(0, 1.0, n_segments + 1)
        bx = (1 - t_vals) ** 2 * x0 + 2 * t_vals * (1 - t_vals) * cx + t_vals**2 * x1
        by = (1 - t_vals) ** 2 * y0 + 2 * t_vals * (1 - t_vals) * cy + t_vals**2 * y1

        c0 = np.array(mcolors.to_rgb(node_colors_map[u]))
        c1 = np.array(mcolors.to_rgb(node_colors_map[v]))
        t_mids = (t_vals[:-1] + t_vals[1:]) / 2
        # Gradient runs destination→source so the edge "arrives" in the source node's colour
        segment_colors = np.clip((1 - t_mids[:, None]) * c1 + t_mids[:, None] * c0, 0, 1)

        points = np.column_stack([bx, by]).reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        ax.add_collection(LineCollection(segments, colors=segment_colors, linewidths=1.5, zorder=1))

        # Arrowhead above nodes (zorder=4) so it's visible at the destination node boundary
        ax.annotate(
            "",
            xy=_bez(x0, y0, cx, cy, x1, y1, 0.88),
            xytext=_bez(x0, y0, cx, cy, x1, y1, 0.81),
            arrowprops=dict(arrowstyle="-|>", color=tuple(0.2 * c0 + 0.8 * c1), lw=0.0, mutation_scale=12),
            zorder=4,
        )


def _draw_edge_labels(ax, graph: nx.DiGraph, pos: dict, node_colors_map: dict, rad: float = 0.1) -> None:
    for u, v, data in graph.edges(data=True):
        label = data.get("label")
        if not label:
            continue
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        if np.hypot(x1 - x0, y1 - y0) < 1e-10:
            continue
        cx, cy = _arc_control(x0, y0, x1, y1, rad)
        lx, ly = _bez(x0, y0, cx, cy, x1, y1, 0.5)
        ax.text(
            lx,
            ly,
            label,
            color=node_colors_map[u],
            fontsize=5.5,
            ha="center",
            va="center",
            fontweight="bold",
            zorder=5,
            bbox=dict(facecolor=_BG_COLOR, edgecolor="none", alpha=0.85, boxstyle="round,pad=0.15"),
        )
