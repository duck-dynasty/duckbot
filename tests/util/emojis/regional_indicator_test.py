import pytest

from duckbot.util.emojis import regional_indicator


@pytest.mark.parametrize("letter,emoji", [(chr(ord("a") + x), chr(x + 0x0001F1E6)) for x in range(0, 26)])
def test_regional_indicator_valid_letter(letter, emoji):
    assert regional_indicator(letter) == emoji


def test_regional_indicator_not_single_char():
    with pytest.raises(AssertionError):
        regional_indicator("aa")


@pytest.mark.parametrize("letter", [chr(x) for x in range(0, 256) if not ord("a") <= x <= ord("z")])
def test_regional_indicator_not_lowercase_alphabet_char(letter):
    with pytest.raises(AssertionError):
        regional_indicator(letter)
