import pytest

from duckbot.slash import Option, OptionType


@pytest.mark.parametrize("name", ["a name", "some\nname", "bruh\tname"])
def test_name_contains_whitespace_throws(name):
    with pytest.raises(ValueError):
        Option(name=name, description="d")


def test_to_dict():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).to_dict() == {
        "name": "n",
        "description": "d",
        "type": OptionType.STRING,
        "required": True,
        "options": [],
    }
