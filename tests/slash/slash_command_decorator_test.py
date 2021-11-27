import pytest
from discord.ext.commands import BadArgument, command

from duckbot.slash import Option, OptionType, slash_command
from duckbot.slash.option import SubCommand


async def func():
    """A nothing function for @command to wrap."""


def test_slash_command_patches_adapt_name():
    cmd = command()(func)
    slash_command(root="root", name="name")(cmd)
    assert cmd._discordpy_include_subcommand_name == {"name": True}


def test_slash_command_patches_adapt_name_as_given_value():
    cmd = command()(func)
    slash_command(root="root", name="name", discordpy_include_subcommand_name=False)(cmd)
    assert cmd._discordpy_include_subcommand_name == {"name": False}


def test_slash_command_patches_adapt_name_to_parent():
    parent = command()(func)
    cmd = command(parent=parent)(func)
    slash_command(root="root", name="name")(cmd)
    assert parent._discordpy_include_subcommand_name == {"name": True}


def test_slash_command_patches_adapt_name_to_parent_as_given_value():
    parent = command()(func)
    cmd = command(parent=parent)(func)
    slash_command(root="root", name="name", discordpy_include_subcommand_name=False)(cmd)
    assert parent._discordpy_include_subcommand_name == {"name": False}


def test_slash_command_patches_adapt_name_to_parent_multiple():
    parent = command()(func)
    cmd1 = command(parent=parent)(func)
    cmd2 = command(parent=parent)(func)
    slash_command(root="root", name="name1")(cmd1)
    slash_command(root="root", name="name2")(cmd2)
    assert parent._discordpy_include_subcommand_name == {"name1": True, "name2": True}


def test_slash_command_patches_copy():
    cmd = command()(func)
    slash_command(root="root", name="name")(cmd)
    copy = cmd.copy()
    assert copy._discordpy_include_subcommand_name == cmd._discordpy_include_subcommand_name
    assert copy.slash_ext == cmd.slash_ext


def test_slash_command_creates_slash_ext():
    slash = slash_command()(command()(func))
    assert slash.slash_ext is not None


def test_slash_command_slash_name_is_root():
    slash = slash_command(root="root", name="name")(command()(func))
    assert slash.slash_ext.name == "root"


def test_slash_command_slash_name_is_command_name():
    slash = slash_command()(command(name="name")(func))
    assert slash.slash_ext.name == "name"


def test_slash_command_slash_description_is_root():
    slash = slash_command(root="root", name="name")(command()(func))
    assert slash.slash_ext.description == "root"


def test_slash_command_slash_description_is_description():
    slash = slash_command(description="desc")(command()(func))
    assert slash.slash_ext.description == "desc"


def test_slash_command_slash_description_is_command_description():
    slash = slash_command()(command(description="desc")(func))
    assert slash.slash_ext.description == "desc"


def test_slash_command_slash_description_is_command_name():
    slash = slash_command()(command(name="name")(func))
    assert slash.slash_ext.description == "name"


def test_slash_command_slash_options_is_empty():
    slash = slash_command()(command()(func))
    assert slash.slash_ext.options == []


def test_slash_command_slash_options_is_provided():
    options = [Option(name="opt")]
    slash = slash_command(options=options)(command()(func))
    assert slash.slash_ext.options == options


def test_slash_command_slash_options_subcommand():
    options = [Option(name="opt")]
    slash = slash_command(root="root", name="name", options=options)(command()(func))
    assert slash.slash_ext.options == [SubCommand(name="name", description=None, type=OptionType.SUB_COMMAND, options=options)]


def test_slash_command_not_decorating_command():
    with pytest.raises(TypeError):

        @slash_command
        class NotACommand:
            pass


def test_slash_command_root_but_no_name():
    with pytest.raises(BadArgument):
        slash_command(root="root", name=None)(command()(func))


def test_slash_command_name_but_no_root():
    with pytest.raises(BadArgument):
        slash_command(root=None, name="name")(command()(func))
