import random

import pytest

from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rates import Rates

items = [Item.IronOre, Item.CopperOre, Item.CateriumOre, Item.Water]


@pytest.fixture(params=items)
def rate(request) -> tuple[Item, float]:
    return (request.param, random.random())


another_rate = rate


def test_init_dict(rate, another_rate):
    d = dict([rate, another_rate])
    rates = Rates(d)
    assert rates.rates == d and rates.rates is not d


def test_items_is_dict_items(rate):
    rates = to_rates(rate)
    assert dict(rates.items()) == dict(rates.rates.items())


def test_keys_is_dict_keys(rate):
    rates = to_rates(rate)
    assert set(rates.keys()) == set(rates.rates.keys())


@pytest.mark.parametrize("item", items)
def test_get_is_dict_get(item, rate):
    rates = to_rates(rate)
    assert rates.get(item, None) == rates.rates.get(item, None)


@pytest.mark.parametrize("item", items)
def test_contains_is_dict_contains(item, rate):
    rates = to_rates(rate)
    assert (item in rates) == (item in rates.rates)


def test_singleton_rate_empty_throws_error():
    with pytest.raises(AssertionError):
        Rates({}).singleton_rate()


def test_singleton_rate_singleton_returns_rate(rate):
    assert to_rates(rate).singleton_rate() == rate[1]


def test_singleton_rate_not_singleton_throws_error():
    with pytest.raises(AssertionError):
        Rates({Item.AdaptiveControlUnit: 1, Item.AiExpansionServer: 1}).singleton_rate()


def test_bool_empty_is_false():
    assert bool(Rates()) is False


def test_bool_nonempty_is_true():
    assert bool(to_rates((Item.IronOre, 30))) is True


def test_eq_equal(rate):
    assert to_rates(rate) == to_rates(rate)


def test_eq_close_rate(rate):
    assert to_rates(rate) == to_rates((rate[0], rate[1] + 1e-12))


def test_eq_different_item(rate):
    items = list(Item)
    rhs = (items[(items.index(rate[0]) + 1) % len(items)], rate[1])
    assert to_rates(rate) != to_rates(rhs)


def test_eq_different_rate(rate):
    assert to_rates(rate) != to_rates((rate[0], rate[1] + 1))


def test_str_returns_dict_string(rate):
    rates = to_rates(rate)
    assert str(rates) == f"Rates({str(rates.rates)})"


def test_repr_returns_dict_string(rate):
    rates = to_rates(rate)
    assert repr(rates) == f"Rates({str(rates.rates)})"


def test_add_returns_combined_rates(rate, another_rate):
    assert to_rates(rate) + to_rates(another_rate) == Rates(dict([rate, another_rate]))


def test_rshift_creates_rates_output(rate, another_rate):
    assert to_rates(rate) >> to_rates(another_rate) == (to_rates(rate), to_rates(another_rate))


def to_rates(rate: tuple[Item, float]) -> Rates:
    return rate[0] * rate[1]
