from dataclasses import dataclass
from typing import Set

from .item import Item
from .rates import Rates
from .recipe import ModifiedRecipe


@dataclass
class Factory:
    inputs: Rates
    recipes: Set[ModifiedRecipe]
    targets: Rates
    maximize: Set[Item]
    power_shards: int = 0
    sloops: int = 0
