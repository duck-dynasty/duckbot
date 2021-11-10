from duckbot.slash import Option, OptionType
from duckbot.slash.option import SubCommand
from duckbot.slash.slash_command import SlashCommand


def test_name_is_root(command):
    assert SlashCommand(command, root="root", name="name", description="description", options=[]).name == "root"


def test_name_is_name(command):
    assert SlashCommand(command, root=None, name="name", description="description", options=[]).name == "name"


def test_name_is_command_name(command):
    command.name = "command"
    assert SlashCommand(command, root=None, name=None, description="description", options=[]).name == "command"


def test_description_is_root(command):
    assert SlashCommand(command, root="root", name="name", description="description", options=[]).description == "root"


def test_description_is_description(command):
    assert SlashCommand(command, root=None, name="name", description="description", options=[]).description == "description"


def test_description_is_command_description(command):
    command.description = "command"
    assert SlashCommand(command, root=None, name="name", description=None, options=[]).description == "command"


def test_description_is_name(command):
    command.description = None
    assert SlashCommand(command, root=None, name="name", description=None, options=[]).description == "name"


def test_options_empty_base_command(command):
    assert SlashCommand(command, root=None, name=None, description="description", options=[]).options == []


def test_options_list_base_command(command):
    clazz = SlashCommand(command, root=None, name=None, description="description", options=[Option(name="opt", description="desc")])
    assert clazz.options == [Option(name="opt", description="desc")]


def test_options_empty_base_command_group_options(command):
    clazz = SlashCommand(command, root=None, name=None, description="description", options=[])
    clazz.append_options([Option(name="opt", description="desc")])
    assert clazz.options == [Option(name="opt", description="desc")]


def test_options_list_base_command_group_options(command):
    clazz = SlashCommand(command, root=None, name=None, description="description", options=[Option(name="opt1", description="desc1")])
    clazz.append_options([Option(name="opt2", description="desc2")])
    assert clazz.options == [Option(name="opt1", description="desc1"), Option(name="opt2", description="desc2")]


def test_options_empty_root_command(command):
    assert SlashCommand(command, root="root", name="name", description="description", options=[]).options == [
        SubCommand(name="name", description="description", type=OptionType.SUB_COMMAND, options=[])
    ]


def test_options_empty_root_command_group_options(command):
    clazz = SlashCommand(command, root="root", name="name", description="description", options=[])
    clazz.append_options([SubCommand(name="name2", description="desc2", type=OptionType.SUB_COMMAND, options=[])])
    assert clazz.options == [
        SubCommand(name="name", description="description", type=OptionType.SUB_COMMAND, options=[]),
        SubCommand(name="name2", description="desc2", type=OptionType.SUB_COMMAND, options=[]),
    ]


def test_to_dict(command):
    clazz = SlashCommand(command, root="root", name="name", description="description", options=[])
    assert clazz.to_dict() == {"name": clazz.name, "description": clazz.description, "options": [x.to_dict() for x in clazz.options]}
