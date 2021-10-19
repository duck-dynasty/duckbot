import typing


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


class Option:
    def __init__(self, *, name: str, description: str = None, type: OptionType = OptionType.STRING, required: bool = False):
        self._name = name
        self._description = description
        self._type = type
        self._required = required

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description or self.name

    @property
    def type(self) -> OptionType:
        return self._type

    @property
    def required(self) -> bool:
        return self._required

    @property
    def options(self) -> typing.List:
        return []

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "type": self.type, "required": self.required, "options": [x.to_dict() for x in self.options]}

    def __eq__(self, other) -> bool:
        return self.to_dict() == other.to_dict() if isinstance(other, Option) else False

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self.to_dict())


class SubCommand(Option):
    def __init__(self, *, name: str, description: str, type: OptionType, options):
        super().__init__(name=name, description=description, type=type, required=False)
        self._options = options

    @property
    def options(self) -> typing.List:
        return self._options

    def __eq__(self, other) -> bool:
        return super().__eq__(other)  # just to make LGTM happy, no real need to override since it uses to_dict()
