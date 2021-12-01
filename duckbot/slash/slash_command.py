import re
from dataclasses import InitVar, asdict, dataclass, field
from typing import List

from discord.ext.commands import Command

from .option import Option, OptionType, SubCommand


@dataclass
class SlashCommand:
    command: InitVar[Command]
    root: InitVar[str] = ""
    name: str = ""
    description: str = ""
    options: List[Option] = field(default_factory=list)

    def __post_init__(self, command, root):
        if not isinstance(command, Command):
            raise TypeError("callback command must be a discord.ext.commands.Command")
        if root and not self.name or not root and self.name:
            raise ValueError("root and name must both be provided if either is")
        if root and re.search(r"\s", root):
            raise ValueError(f"slash command root name cannot contain whitespace: {root}")
        if self.name and re.search(r"\s", self.name):
            raise ValueError(f"slash command name cannot contain whitespace: {self.name}")

        is_root_command = root and self.name
        if is_root_command:  # group options before changing the name/description of the overall command
            self.options = [SubCommand(name=self.name, description=self.description, type=OptionType.SUB_COMMAND, options=self.options)]

        self.name = root or self.name or command.name
        self.description = root or self.description or command.description or self.name

    def append_options(self, group_opts: List[Option]):
        self.options = self.options + group_opts

    def to_dict(self) -> dict:
        return asdict(self)
