from duckbot.slash import Option, OptionType
from duckbot.slash.option import SubCommand

option = Option(name="a", description="b", type=OptionType.STRING, required=True)


def test_name_getter():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).name == "n"


def test_description_getter_valid_description():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).description == "d"


def test_name_getter_invalid_description():
    assert SubCommand(name="n", description=None, type=OptionType.SUB_COMMAND, options=[option]).description == "n"


def test_type_getter():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).type == OptionType.SUB_COMMAND


def test_required_getter():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).required == False


def test_options_getter():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).options == [option]


def test_to_dict():
    assert SubCommand(name="n", description="d", type=OptionType.SUB_COMMAND, options=[option]).to_dict() == {
        "name": "n",
        "description": "d",
        "type": OptionType.SUB_COMMAND,
        "required": False,
        "options": [option.to_dict()],
    }
