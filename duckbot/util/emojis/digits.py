def digit(n: int) -> str:
    """Returns the emoji for a given digit."""
    assert 0 <= n <= 9
    zero = 0x00000030
    return chr(zero + n) + chr(0x000020E3)
