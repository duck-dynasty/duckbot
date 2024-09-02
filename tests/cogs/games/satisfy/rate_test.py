import random

import pytest

from duckbot.cogs.games.satisfy.item import Item
from duckbot.cogs.games.satisfy.rate import Rate, Rates


@pytest.fixture(params=[x for x in Item])
def rate(request):
    return Rate(request.param, random.random())


another_rate = rate


def test_tuple_returns_values(rate):
    assert rate.tuple() == (rate.item, rate.rate)


def test_eq_equal(rate):
    rhs = Rate(rate.item, rate.rate)
    assert rate == rhs


def test_eq_different_item(rate):
    items = list(Item)
    rhs = Rate(items[(items.index(rate.item) + 1) % len(items)], rate.rate)
    assert rate != rhs


def test_eq_different_rate(rate):
    assert rate != Rate(rate.item, rate.rate + 1)


def test_str_returns_tuple_string(rate):
    assert str(rate) == str(rate.tuple())


def test_repr_returns_tuple_string(rate):
    assert repr(rate) == str(rate.tuple())


def test_add_returns_combined_rates(rate, another_rate):
    assert rate + another_rate == Rates([rate, another_rate])


def test_rshift_rate_creates_rates_output(rate, another_rate):
    assert rate >> another_rate == (Rates([rate]), Rates([another_rate]))


def test_rshift_rates_copies_rates_output(rate, another_rate):
    rates = Rates([another_rate])
    assert rate >> rates == (Rates([rate]), rates)
