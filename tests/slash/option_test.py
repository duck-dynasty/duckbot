from duckbot.slash import Option, OptionType


def test_name_getter():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).name == "n"


def test_description_getter_valid_description():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).description == "d"


def test_name_getter_invalid_description():
    assert Option(name="n", description=None, type=OptionType.STRING, required=True).description == "n"


def test_type_getter():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).type == OptionType.STRING


def test_required_getter():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).required


def test_options_getter():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).options == []


def test_to_dict():
    assert Option(name="n", description="d", type=OptionType.STRING, required=True).to_dict() == {
        "name": "n",
        "description": "d",
        "type": OptionType.STRING,
        "required": True,
        "options": [],
    }


def test_equals_equal():
    a = Option(name="n", description="d", type=OptionType.STRING, required=True)
    b = Option(name="n", description="d", type=OptionType.STRING, required=True)
    assert a == b


def test_equals_fields_different():
    a = Option(name="n", description="d", type=OptionType.STRING, required=True)
    b = Option(name="a", description="b", type=OptionType.STRING, required=True)
    assert a != b


def test_equals_different_class():
    a = Option(name="n", description="d", type=OptionType.STRING, required=True)
    b = "str"
    assert a != b


def test_str_is_dict_str():
    opt = Option(name="n", description="d", type=OptionType.STRING, required=True)
    assert str(opt) == str(opt.to_dict())


def test_repr_is_dict_str():
    opt = Option(name="n", description="d", type=OptionType.STRING, required=True)
    assert repr(opt) == str(opt.to_dict())
