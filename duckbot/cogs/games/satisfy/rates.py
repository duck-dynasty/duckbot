from __future__ import annotations

from math import isclose
from typing import Optional

from .item import Item


class Rates:
    def __init__(self, rates: dict[Item, float] = dict()):
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
        if not isinstance(rhs, Rates) or set(self.rates.keys()) != set(rhs.rates.keys()):
            return False
        else:
            return all([isclose(l, rhs.rates[i]) for i, l in self.items()])

    def __add__(self, rates: Rates) -> Rates:
        return Rates(self.rates | rates.rates)

    def __rshift__(self, output: Rates) -> tuple[Rates, Rates]:
        return (self, output)

    def __mul__(self, scale_factor: float) -> Rates:
        return Rates(dict((i, r * scale_factor) for i, r in self.items()))

    def __str__(self) -> str:
        return f"Rates({str(self.rates)})"

    def __repr__(self) -> str:
        return str(self)
