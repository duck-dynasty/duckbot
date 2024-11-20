import pytest
from discord import Embed

from duckbot.util.embeds import group_by_max_length


def embed(length: int) -> Embed:
    return Embed(title=f"{length}" + "_" * (length - len(f"{length}")))


@pytest.mark.parametrize("length", [1, 2, 3, 3000, 6001])
def test_embed_length(length):
    assert len(embed(length)) == length


@pytest.mark.parametrize(
    "lengths, expected_indexes",
    [
        ([], []),  # empty
        ([1], [[0]]),  # trivial singleton
        ([2000, 2000], [[0, 1]]),  # fits in single message
        ([3000, 2999], [[0, 1]]),  # just fits in single message
        ([3000, 3000], [[0], [1]]),  # equal to max; separates
        ([4000, 4000], [[0], [1]]),  # each gets put into own message
        ([2500, 2500, 2500], [[0, 1], [2]]),  # single embed leftover in new message
        ([4000, 2500, 2500], [[0], [1, 2]]),  # multiple leftover in new message
        ([4000, 2500, 4000, 2500], [[0], [1], [2], [3]]),  # can never add subsequent embed into message
    ],
)
def test_group_by_max_length_all_cases(lengths, expected_indexes):
    embeds = [embed(length) for length in lengths]
    expected = [[embeds[i] for i in group] for group in expected_indexes]
    assert group_by_max_length(embeds) == expected
