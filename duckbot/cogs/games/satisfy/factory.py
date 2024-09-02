from dataclasses import dataclass
from typing import List, Set

from .item import Item
from .recipe import Recipe


@dataclass
class Factory:
    inputs: dict[Item, float]
    recipes: List[Recipe]
    targets: dict[Item, float]
    maximize: Set[Item]
