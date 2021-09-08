from duckbot.util.emojis import red_a, red_b, regional_indicator

phrases = [
    [  # car go fast
        regional_indicator("c"),
        regional_indicator("a"),
        regional_indicator("r"),
        regional_indicator("g"),
        regional_indicator("o"),
        regional_indicator("f"),
        red_a(),
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
        red_b(),
        regional_indicator("i"),
        regional_indicator("n"),
    ],
    [regional_indicator("h"), regional_indicator("y"), regional_indicator("p"), regional_indicator("e")],
    [regional_indicator("p"), regional_indicator("o"), regional_indicator("g")],
    [regional_indicator("d"), regional_indicator("a"), regional_indicator("n"), regional_indicator("k")],
    [regional_indicator("b"), red_a(), regional_indicator("n"), regional_indicator("g")],
]
