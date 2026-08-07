import pytest
from discord.app_commands import Choice

from duckbot.util.choices import choices


def choice(value: str) -> Choice:
    return Choice(name=value, value=value)


@pytest.mark.parametrize("min_characters", range(1, 10))
def test_choices_below_min_characters_returns_empty(min_characters):
    assert choices([], "x" * (min_characters - 1), min_characters=min_characters) == []


@pytest.mark.parametrize("substr", ["substr"[i:j] for i in range(6) for j in range(i + 1, 6 + 1)])
def test_choices_substring_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, min_characters=0) == [choice("substr")]


@pytest.mark.parametrize("substr", ["SUBSTR"[i:j] for i in range(6) for j in range(i + 1, 6 + 1)])
def test_choices_substring_case_different_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, min_characters=0) == [choice("substr")]


@pytest.mark.parametrize("substr", ["sub", "SUB", "sbt", "sBT"])
def test_choices_same_characters_in_same_order_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, min_characters=0) == [choice("substr")]


@pytest.mark.parametrize("substr", ["sbt", "sBT", "sur", "ubr"])
def test_choices_not_in_order_gapped_needle_returns_no_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, min_characters=0, in_order=False) == []


@pytest.mark.parametrize("substr", ["subs", "SUBS", "bst", "BsT"])
def test_choices_not_in_order_whole_needle_returns_matches(substr):
    pool = ["substr", "nope"]
    assert choices(pool, substr, min_characters=0, in_order=False) == [choice("substr")]


def test_choices_returns_at_most_25_elements():
    pool = [f"string-{x}" for x in range(50)]
    assert len(choices(pool, "string", min_characters=0)) == 25
