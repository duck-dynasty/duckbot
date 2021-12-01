import pytest

from duckbot.slash import Option, OptionType
from duckbot.slash.option import SubCommand

option = Option(name="a", description="b", type=OptionType.STRING, required=True)


@pytest.mark.parametrize("name", ["a name", "some\nname", "bruh\tname"])
def test_name_contains_whitespace_throws(name):
    with pytest.raises(ValueError):
        SubCommand(name=name, description="d", options=[option])


def test_to_dict():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).to_dict() == {
        "name": "n",
        "description": "d",
        "type": OptionType.SUB_COMMAND,
        "required": False,
        "options": [option.to_dict()],
    }
