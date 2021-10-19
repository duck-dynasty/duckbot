from typing import List

from discord.ext.commands import Command

from .option import Option, OptionType, SubCommand


class SlashCommand:
    def __init__(self, command: Command, *, root: str, name: str, description: str, options: List[Option]):
        self._command = command
        self._root = root
        self._name = name
        self._description = description
        self._options = options
        self._group_options = []

    @property
    def name(self) -> str:
        return self._root or self._name or self._command.name

    @property
    def description(self) -> str:
        return self._root or self._description or self._command.description or self.name

    @property
    def options(self) -> List[Option]:
        if self._root and self._name:
            opts = [SubCommand(name=self._name, description=self._description, type=OptionType.SUB_COMMAND, options=self._options)]
        else:
            opts = self._options
        return opts + self._group_options

    def append_options(self, group_opts: List[Option]):
        self._group_options += group_opts

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "options": [x.to_dict() for x in self.options]}
