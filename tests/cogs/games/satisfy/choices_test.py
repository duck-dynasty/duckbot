import pytest
from discord.app_commands import Choice

from duckbot.cogs.games.satisfy.satisfy import choices


def choice(value: str) -> Choice:
    return Choice(name=value, value=value)


@pytest.mark.parametrize("threshold", range(1, 10))
def test_choices_below_threshold_returns_empty(threshold):
    assert choices([], "x" * (threshold - 1), threshold=threshold) == []


@pytest.mark.parametrize("substr", ["substr"[i:j] for i in range(6) for j in range(i + 1, 6 + 1)])
def test_choices_substring_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, threshold=0) == [choice("substr")]


@pytest.mark.parametrize("substr", ["SUBSTR"[i:j] for i in range(6) for j in range(i + 1, 6 + 1)])
def test_choices_substring_case_different_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, threshold=0) == [choice("substr")]


@pytest.mark.parametrize("substr", ["sub", "SUB", "sbt", "sBT"])
def test_choices_same_characters_in_same_order_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, threshold=0) == [choice("substr")]
