from __future__ import annotations

from math import isclose
from typing import List, Optional

from .item import Item


class Rate:
    def __init__(self, item: Item, rate: float):
        self.item = item
        self.rate = rate

    def tuple(self) -> tuple[Item, float]:
        return (self.item, self.rate)

    def __eq__(self, rhs: object) -> bool:
        return False if not isinstance(rhs, Rate) else self.item == rhs.item and isclose(self.rate, rhs.rate)

    def __add__(self, rhs: Rate) -> Rates:
        return Rates([self, rhs])

    def __rshift__(self, output: Rate | Rates) -> tuple[Rates, Rates]:
        return (Rates([self]), output if isinstance(output, Rates) else Rates([output]))

    def __str__(self) -> str:
        return str(self.tuple())

    def __repr__(self) -> str:
        return str(self)


class Rates:
    def __init__(self, rates: List[Rate] | dict[Item, float] = []):
        self.rates = dict(rates if isinstance(rates, dict) else [r.tuple() for r in rates])

    def items(self):
        return self.rates.items()

    def __iter__(self):
        return self.rates.__iter__()

    def get(self, key: Item, default: Optional[float]) -> Optional[float]:
        return self.rates.get(key, default)

    def __bool__(self) -> bool:
        return bool(self.rates)

    def __eq__(self, rhs: object) -> bool:
        return False if not isinstance(rhs, Rates) else self.rates == rhs.rates

    def __add__(self, rate: Rate) -> Rates:
        x = self.rates.copy()
        x[rate.item] = rate.rate
        return Rates(x)

    def __rshift__(self, output: Rate | Rates) -> tuple[Rates, Rates]:
        return (self, output if isinstance(output, Rates) else Rates([output]))

    def __mul__(self, scale_factor: float) -> Rates:
        return Rates(dict((i, r * scale_factor) for i, r in self.items()))

    def __str__(self) -> str:
        return str(self.rates)

    def __repr__(self) -> str:
        return str(self)
