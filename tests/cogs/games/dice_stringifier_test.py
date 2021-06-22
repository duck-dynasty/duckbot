import d20

from duckbot.cogs.games.dice import DiceStringifier


def test_str_expression_stringifies_node_roll_non_crit():
    result = d20.roll("1d20", stringifier=DiceStringifier())
    while result.crit != d20.CritType.NONE:
        result = d20.roll("1d20", stringifier=DiceStringifier())
    assert result.result == f"1d20 ({result.total})"


def test_str_expression_stringifies_node_roll_crit():
    result = d20.roll("1d20", stringifier=DiceStringifier())
    while result.crit == d20.CritType.NONE:
        result = d20.roll("1d20", stringifier=DiceStringifier())
    assert result.result == f"1d20 (**{result.total}**)"
