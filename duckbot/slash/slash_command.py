import typing

from discord.ext.commands import Command
from discord.ext.commands.errors import BadArgument

from duckbot.slash.option import Option, OptionType


class SubCommand:
    def __init__(self, *, name: str, description: str, type: OptionType, options):
        self.name = name
        self.description = description
        self.type = type
        self.options = options
        self.__dict__ = {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "required": False,
            "options": [x.__dict__ for x in self.options],
        }


class SlashCommand:
    def __init__(self, command: Command, *, root: str, name: str, description: str, options: typing.List[Option]):
        self._command = command
        self._root = root
        self._name = name
        self._description = description
        self._options = options

    @property
    def name(self):
        return self._root or self._name or self._command.name

    @property
    def description(self):
        return self._root or self._description or self._command.description or self.name

    @property
    def options(self):
        if self._root and self._name:
            return [SubCommand(name=self._name, description=self._description, type=OptionType.SUB_COMMAND, options=self._options)]
        else:
            return self._options


def slash_command(*, root: str = None, name: str = None, description: str = None, options: typing.List[Option] = [], discordpy_adapt_name: bool = True):
    """Returns a discord-py command as a slash command as well."""

    def decorator(command):
        if not isinstance(command, Command):
            raise TypeError("callback must be a discord.ext.commads.Command")
        if root and not name or not root and name:
            raise BadArgument("root and name must both be provided if either is")

        # patch the command instance with extra info so we can register it with discord
        command.slash_ext = SlashCommand(command, root=root, name=name, description=description, options=options)

        if not hasattr(command, "_slash_discordpy_adapt_name"):
            command._slash_discordpy_adapt_name = {}
        command._slash_discordpy_adapt_name[name] = discordpy_adapt_name
        if command.parent:
            if not hasattr(command.parent, "_slash_discordpy_adapt_name"):
                command.parent._slash_discordpy_adapt_name = {}
            command.parent._slash_discordpy_adapt_name[name] = discordpy_adapt_name

        # override copy to keep the patched slash properties
        original_copy = command.copy

        def copy():
            c = original_copy()
            c.slash_ext = command.slash_ext
            c._slash_discordpy_adapt_name = command._slash_discordpy_adapt_name
            return c

        command.copy = copy
        return command

    return decorator
