from dataclasses import dataclass, field
from typing import Dict, Set

from .item import Item
from .rates import Rates
from .recipe import ModifiedRecipe


@dataclass
class Factory:
    inputs: Rates = field(default_factory=Rates)
    targets: Rates = field(default_factory=Rates)
    maximize: Set[Item] = field(default_factory=set)
    recipes: Set[ModifiedRecipe] = field(default_factory=set)
    limits: Dict[ModifiedRecipe, float] = field(default_factory=dict)
    power_shards: int = 0
    sloops: int = 0
