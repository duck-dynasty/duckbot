from duckbot.util.emojis import red_a, red_b


def test_red_a_returns_a():
    assert red_a() == "\U0001F170"


def test_red_b_returns_b():
    assert red_b() == "\U0001F171"
