import random

import pytest

from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rate import Rate


@pytest.mark.parametrize("item", Item)
def test_str_returns_enum_name(item: Item):
    assert str(item) == item.name


@pytest.mark.parametrize("item", Item)
def test_repr_returns_enum_name(item: Item):
    assert repr(item) == item.name


@pytest.mark.parametrize("item", Item)
def test_mul_returns_rate_tuple(item: Item):
    n = random.random()
    assert item * n == Rate(item, n)
