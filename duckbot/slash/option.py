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


class Option:
    def __init__(self, *, name: str, description: str = None, option_type: OptionType = OptionType.STRING, required: bool = False):
        self.name = name
        self.description = description if description is not None else name
        self.type = option_type
        self.required = required
