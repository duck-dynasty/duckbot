from dataclasses import dataclass, field
from typing import Dict, List, Set

from .item import Item
from .rates import Rates
from .recipe import ModifiedRecipe


@dataclass
class Factory:
    inputs: Rates = field(default_factory=Rates)
    targets: Rates = field(default_factory=Rates)
    maximize: List[Item] = field(default_factory=list)
    recipes: Set[ModifiedRecipe] = field(default_factory=set)
    limits: Dict[ModifiedRecipe, float] = field(default_factory=dict)
    power_shards: int = 0
    sloops: int = 0
