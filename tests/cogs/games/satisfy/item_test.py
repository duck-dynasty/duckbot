import random
from math import inf

import pytest

from duckbot.cogs.games.satisfy.item import Form, Item, sinkable, transport_limit
from duckbot.cogs.games.satisfy.rates import Rates


@pytest.mark.parametrize("item", Item)
def test_str_returns_enum_name(item: Item):
    assert str(item) == item.name


@pytest.mark.parametrize("item", Item)
def test_repr_returns_enum_name(item: Item):
    assert repr(item) == item.name


@pytest.mark.parametrize("item", Item)
def test_mul_returns_rates(item: Item):
    n = random.random()
    assert item * n == Rates(dict([(item, n)]))


@pytest.mark.parametrize("item", Item)
def test_lt_alphabetical_order_by_name(item: Item):
    rhs = random.choice([x for x in Item])
    assert (item < rhs) == (item.name < rhs.name)


@pytest.mark.parametrize("item", [i for i in Item if i.form == Form.Solid])
def test_transport_limit_solid_is_belt_limit(item: Item):
    assert transport_limit(item) == 1200


@pytest.mark.parametrize("item", [i for i in Item if i.form == Form.Fluid])
def test_transport_limit_fluid_is_pipe_limit(item: Item):
    assert transport_limit(item) == 600


@pytest.mark.parametrize("item", [i for i in Item if i.form == Form.Aux])
def test_transport_limit_aux_is_infinite(item: Item):
    assert transport_limit(item) == inf


@pytest.mark.parametrize("item", [i for i in Item if i.form != Form.Solid])
def test_sinkable_nonsolid_returns_false(item: Item):
    assert sinkable(item) is False


@pytest.mark.parametrize("item", [i for i in Item if i.points == 0])
def test_sinkable_nonpoints_returns_false(item: Item):
    assert sinkable(item) is False


@pytest.mark.parametrize("item", [i for i in Item if i.form == Form.Solid and i.points != 0])
def test_sinkable_solid_and_nonzero_points_returns_true(item: Item):
    assert sinkable(item) is True
