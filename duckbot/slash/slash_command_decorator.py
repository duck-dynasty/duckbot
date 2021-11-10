from typing import List, Optional

from discord.ext.commands import BadArgument, Command

from .option import Option
from .slash_command import SlashCommand


def get_slash_command(command: Command) -> Optional[SlashCommand]:
    """Returns the SlashCommand contained in the discord.py command, if any. Returns None
    if the command does not wrap a slash command.
    :param: command the discord.py command
    :return: the wrapped SlashCommand or None if it does not exist"""
    return command.slash_ext if hasattr(command, "slash_ext") and command.slash_ext else None


def slash_command(*, root: str = None, name: str = None, description: str = None, options: List[Option] = [], discordpy_include_subcommand_name: bool = True):
    """A decorator to mark a discord.py command as a discord slash command (aka interaction).
    :param root: the command basename, for use with sub-commands; if provided, `name` must also be provided
    :param name: the name to create the command with; if provided, `name` must also be provided
    :param description: the command description; a short blurb about what the command does; defaults to the command description.
    :param options: the slash command options
    :param discordpy_include_subcommand_name: True to include subcommand names in the discord.py delegate, False to exclude the subcommand name
    :return: the decorated Command, with new fields for slash command specifics added
    """

    def decorator(command):
        if not isinstance(command, Command):
            raise TypeError("callback must be a discord.ext.commads.Command")
        if root and not name or not root and name:
            raise BadArgument("root and name must both be provided if either is")

        # patch the command instance with extra info so we can register it with discord and delegate executions to the discord.py command
        command.slash_ext = SlashCommand(command, root=root, name=name, description=description, options=options)
        command._discordpy_include_subcommand_name = {name: discordpy_include_subcommand_name}
        if hasattr(command, "parent") and command.parent:
            if not hasattr(command.parent, "_discordpy_include_subcommand_name"):
                command.parent._discordpy_include_subcommand_name = {}
            command.parent._discordpy_include_subcommand_name[name] = discordpy_include_subcommand_name

        # override copy to keep the patched slash properties
        original_copy = command.copy

        def copy():
            c = original_copy()
            c.slash_ext = command.slash_ext
            c._discordpy_include_subcommand_name = command._discordpy_include_subcommand_name
            return c

        command.copy = copy
        return command

    return decorator
