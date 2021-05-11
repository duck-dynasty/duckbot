import typing
from discord.ext.commands import Command, Bot, Cog
from discord.ext.commands.view import StringView
from discord.http import Route
from duckbot.slash import Interaction


class Route8(Route):
    BASE = "https://discord.com/api/v8"


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


def slash_command(*, options: typing.List[Option] = []):
    def decorator(command):
        if not isinstance(command, Command):
            raise TypeError("callback must be a discord.ext.commads.Command")
        command.slash_ext = True
        command._slash_options = options
        original_copy = command.copy

        def copy():
            c = original_copy()
            c.slash_ext = command.slash_ext
            c._slash_options = command._slash_options
            return c

        command.copy = copy
        return command

    return decorator


class InteractionContext:
    def __init__(self, *, bot, interaction, command):
        self.bot = bot
        self.interaction = interaction
        self.channel = interaction.channel
        self.guild = interaction.guild
        self.author = interaction.author
        self.command = command
        self.view = StringView(" ".join([x.get("value", "") for x in interaction.data.get("options", [])]))

    async def send(self, content=None, *, embed=None):
        route = Route8("POST", f"/interactions/{self.interaction.id}/{self.interaction.token}/callback")
        json = {"type": 4, "data": {"content": content}}
        await self.bot.http.request(route, json=json)


class SlashCommandPatch(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        bot._connection.parsers["INTERACTION_CREATE"] = self.parse_interaction_create

    def parse_interaction_create(self, data):
        interaction = Interaction(bot=self.bot, data=data)
        self.bot.dispatch("slash", interaction)

    @Cog.listener("on_slash")
    async def handle_slash_interaction(self, interaction: Interaction):
        for command in self.bot.commands:
            if hasattr(command, "slash_ext") and command.slash_ext is True and command.name == interaction.data["name"]:
                context = InteractionContext(bot=self.bot, interaction=interaction, command=command)
                await command.invoke(context)

    @Cog.listener("on_ready")
    async def register_commands(self):
        create_requests = []
        for command in self.bot.commands:
            if not command.hidden and hasattr(command, "slash_ext") and command.slash_ext is True:
                route = Route8("POST", f"/applications/{self.bot.user.id}/commands")
                json = {
                    "name": command.name,
                    "description": command.description if command.description != "" else command.name,
                    "options": [x.__dict__ for x in command._slash_options],
                }
                create_requests.append(json)

        raw_slash = await self.bot.http.request(Route8("GET", f"/applications/{self.bot.user.id}/commands"))
        existing = self.convert_response(raw_slash)
        expected_names = [x["name"] for x in create_requests]
        needs_update = [x for x in create_requests if x not in existing]
        needs_delete = [x for x in existing if x["name"] not in expected_names]

        for x in needs_update:
            route = Route8("POST", f"/applications/{self.bot.user.id}/commands")
            await self.bot.http.request(route, json=x)
        for x in needs_delete:
            id = next(y for y in raw_slash if y["name"] == x["name"])
            route = Route8("DELETE", f"/applications/{self.bot.user.id}/commands/{id}")
            await self.bot.http.request(route)

    def convert_response(self, raw_slash):
        return [
            {
                "name": c["name"],
                "description": c["description"],
                "options": [
                    {
                        "name": o["name"],
                        "description": o["description"],
                        "type": o["type"],
                        "required": o.get("required", False),
                    }
                    for o in c.get("options", [])
                ],
            }
            for c in raw_slash
        ]


def patch_slash_commands(bot: Bot):
    bot._patch_slash_commands = SlashCommandPatch(bot)
    bot.add_cog(bot._patch_slash_commands)
