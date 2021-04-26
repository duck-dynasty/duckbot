# alternate letter emojis
red_a = "\U0001F170"
red_b = "\U0001F171"


def regional_indicator(letter):
    assert len(letter) == 1 and "a" <= letter <= "z"
    regional_indicator_a = 0x0001F1E6
    return chr(ord(letter) - ord("a") + regional_indicator_a)


phrases = [
    [  # car go fast
        regional_indicator("c"),
        regional_indicator("a"),
        regional_indicator("r"),
        regional_indicator("g"),
        regional_indicator("o"),
        regional_indicator("f"),
        red_a,
        regional_indicator("s"),
        regional_indicator("t"),
    ],
    [  # vet go sbin
        regional_indicator("v"),
        regional_indicator("e"),
        regional_indicator("t"),
        regional_indicator("g"),
        regional_indicator("o"),
        regional_indicator("s"),
        red_b,
        regional_indicator("i"),
        regional_indicator("n"),
    ],
    [regional_indicator("h"), regional_indicator("y"), regional_indicator("p"), regional_indicator("e")],
    [regional_indicator("p"), regional_indicator("o"), regional_indicator("g")],
]
