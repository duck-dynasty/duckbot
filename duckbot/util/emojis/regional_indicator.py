def regional_indicator(letter):
    """Returns :regional_indicator_{letter}: emoji for the given letter."""
    assert len(letter) == 1 and "a" <= letter <= "z"
    regional_indicator_a = 0x0001F1E6
    return chr(ord(letter) - ord("a") + regional_indicator_a)
