from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import List


class OptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10


@dataclass(frozen=True)
class Option:
    name: str
    description: str
    options: List[Option] = field(default_factory=list, init=False)
    type: OptionType = OptionType.STRING
    required: bool = False

    def __post_init__(self):
        if re.search(r"\s", self.name):
            raise ValueError(f"option name cannot contain whitespace: {self.name}")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SubCommand(Option):
    options: List[Option]
