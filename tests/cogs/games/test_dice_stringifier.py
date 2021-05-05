import pytest
import d20
from duckbot.cogs.games.dice import DiceStringifier


@pytest.mark.repeat(100)
def test_str_expression_stringifies_node_roll():
    result = d20.roll("1d20", stringifier=DiceStringifier())
    expected = f"1d20 ({result.total})" if result.crit == d20.CritType.NONE else f"1d20 (**{result.total}**)"
    assert result.result == expected
