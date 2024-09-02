import random

import pytest

from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rate import Rate, Rates


@pytest.fixture(params=[x for x in Item])
def rate(request):
    return Rate(request.param, random.random())


another_rate = rate


def test_init_list(rate, another_rate):
    assert Rates([rate, another_rate]).rates == dict([rate.tuple(), another_rate.tuple()])


def test_init_dict(rate, another_rate):
    d = dict([rate.tuple(), another_rate.tuple()])
    rates = Rates(d)
    assert rates.rates == d and rates.rates is not d


def test_items_is_dict_items(rate):
    rates = Rates([rate])
    assert dict(rates.items()) == dict(rates.rates.items())


@pytest.mark.parametrize("item", Item)
def test_get_is_dict_get(item, rate):
    rates = Rates([rate])
    assert rates.get(item, None) == rates.rates.get(item, None)


def test_bool_empty_is_false():
    assert bool(Rates()) is False


def test_bool_nonempty_is_true(rate):
    assert bool(Rates([rate])) is True


def test_eq_equal(rate):
    assert Rates([rate]) == Rates(dict([rate.tuple()]))


def test_eq_different_item(rate):
    items = list(Item)
    rhs = Rate(items[(items.index(rate.item) + 1) % len(items)], rate.rate)
    assert Rates([rate]) != Rates([rhs])


def test_eq_different_rate(rate):
    assert Rates([rate]) != Rates([Rate(rate.item, rate.rate + 1)])


def test_str_returns_dict_string(rate):
    rates = Rates([rate])
    assert str(rates) == str(rates.rates)


def test_repr_returns_dict_string(rate):
    rates = Rates([rate])
    assert repr(rates) == str(rates.rates)


def test_add_returns_combined_rates(rate, another_rate):
    assert Rates([rate]) + another_rate == Rates([rate, another_rate])


def test_rshift_rate_creates_rates_output(rate, another_rate):
    assert Rates([rate]) >> another_rate == (Rates([rate]), Rates([another_rate]))


def test_rshift_rates_copies_rates_output(rate, another_rate):
    rates = Rates([another_rate])
    assert Rates([rate]) >> rates == (Rates([rate]), rates)
