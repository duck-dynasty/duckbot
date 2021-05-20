import pytest
from discord.ext.commands import BadArgument, command

from duckbot.slash import Option, slash_command


async def func(*args):
    pass


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
    assert slash.slash_ext.options == options


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
