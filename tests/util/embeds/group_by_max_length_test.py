import pytest
from discord import Embed

from duckbot.util.embeds import group_by_max_length


def embed(length: int) -> Embed:
    return Embed(title="a" * length)


@pytest.mark.parametrize("length", [0, 1, 3000, 6001])
def test_embed_length(length):
    assert len(embed(length)) == length


def test_empty_returns_empty():
    assert group_by_max_length([]) == []


def test_singleton_returns_singleton():
    e = embed(1)
    assert group_by_max_length([e]) == [[e]]


def test_multiple_fits_in_single_message_returns_single_group():
    e1 = embed(1)
    e2 = embed(2)
    assert group_by_max_length([e1, e2]) == [[e1, e2]]


def test_multiple_does_not_fit_in_single_message_returns_groups():
    e1 = embed(4000)
    e2 = embed(4000)
    assert group_by_max_length([e1, e2]) == [[e1], [e2]]
