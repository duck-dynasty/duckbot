import pytest

from duckbot.util.emojis import digit


@pytest.mark.parametrize("n,emoji", [(x, chr(x + 0x30) + "\U000020e3") for x in range(0, 10)])
def test_digit_valid_number(n, emoji):
    assert digit(n) == emoji


@pytest.mark.parametrize("n", [-1, 10])
def test_digit_invalid_number(n, emoji):
    with pytest.raises(AssertionError):
        assert digit(n)
