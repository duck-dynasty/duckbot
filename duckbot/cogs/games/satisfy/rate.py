from __future__ import annotations

from typing import List, Optional

from .item import Item


class Rate:
    def __init__(self, item: Item, rate: float):
        self.item = item
        self.rate = rate

    def tuple(self) -> tuple[Item, float]:
        return (self.item, self.rate)

    def __add__(self, rhs: Rate | tuple[Item, float]) -> Rates:
        return Rates([self.tuple(), rhs.tuple() if isinstance(rhs, Rate) else rhs])

    def __rshift__(self, output: Rate | tuple[Item, float] | Rates) -> tuple[Rates, Rates]:
        if isinstance(output, Rates):
            return (Rates([self.tuple()]), output)
        else:
            return (Rates([self.tuple()]), Rates([output.tuple() if isinstance(output, Rate) else output]))

    def __str__(self) -> str:
        return str(self.tuple())

    def __repr__(self) -> str:
        return str(self)


class Rates:
    def __init__(self, rates: List[tuple[Item, float]] | dict[Item, float] = []):
        self.rates = dict(rates)

    def items(self):
        return self.rates.items()

    def __iter__(self):
        return self.rates.__iter__()

    def get(self, key: Item, default: Optional[float]) -> Optional[float]:
        return self.rates.get(key, default)

    def __bool__(self) -> bool:
        return bool(self.rates)

    def __add__(self, rate: Rate) -> Rates:
        x = self.rates.copy()
        x[rate.item] = rate.rate
        return Rates(x)

    def __rshift__(self, output: Rate | tuple[Item, float] | Rates) -> tuple[Rates, Rates]:
        if isinstance(output, Rates):
            return (self, output)
        else:
            return (self, Rates([output.tuple() if isinstance(output, Rate) else output]))

    def __str__(self) -> str:
        return str(self.rates)

    def __repr__(self) -> str:
        return str(self)
