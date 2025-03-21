from duckbot.util.emojis import digit, red_a, red_b, regional_indicator


def phrases(supermax):
    return [
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
        [  # fu I mean 1
            regional_indicator("f"),
            regional_indicator("u"),
            regional_indicator("i"),
            regional_indicator("m"),
            regional_indicator("e"),
            regional_indicator("a"),
            regional_indicator("n"),
            digit(1),
        ],
        # hype
        [regional_indicator("h"), regional_indicator("y"), regional_indicator("p"), regional_indicator("e")],
        # pog
        [regional_indicator("p"), regional_indicator("o"), regional_indicator("g")],
        # dank
        [regional_indicator("d"), regional_indicator("a"), regional_indicator("n"), regional_indicator("k")],
        # bAng
        [regional_indicator("b"), red_a(), regional_indicator("n"), regional_indicator("g")],
        # :supermax: washed
        [
            supermax,
            regional_indicator("w"),
            regional_indicator("a"),
            regional_indicator("s"),
            regional_indicator("h"),
            regional_indicator("e"),
            regional_indicator("d"),
        ],
        # San Diego
        [
            regional_indicator("s"),
            regional_indicator("a"),
            regional_indicator("n"),
            regional_indicator("d"),
            regional_indicator("i"),
            regional_indicator("e"),
            regional_indicator("g"),
            regional_indicator("o"),
        ],
    ]
