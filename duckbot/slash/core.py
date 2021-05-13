import typing
from discord.ext.commands import Command, Bot, Cog
from discord.ext.commands.errors import BadArgument
from discord.ext.commands.view import StringView
from duckbot.slash import Interaction, Option, OptionType
from .route import Route8
from .context import InteractionContext


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


def slash_command(*, root: str = None, name: str = None, description: str = None, options: typing.List[Option] = [], discordpy_adapt_name: bool = True):
    def decorator(command):
        if not isinstance(command, Command):
            raise TypeError("callback must be a discord.ext.commads.Command")
        command.slash_ext = True
        if root and not name or not root and name:
            raise BadArgument("root and name must both be provided if either is")
        if root and name:
            command._slash_description = root
            command._slash_name = root
            command._slash_options = [SubCommand(name=name, description=description, type=OptionType.SUB_COMMAND, options=options)]
        else:
            command._slash_description = description
            command._slash_name = name
            command._slash_options = options

        if not hasattr(command, "_slash_discordpy_adapt_name"):
            command._slash_discordpy_adapt_name = {}
        command._slash_discordpy_adapt_name[name] = discordpy_adapt_name
        if command.parent:
            if not hasattr(command.parent, "_slash_discordpy_adapt_name"):
                command.parent._slash_discordpy_adapt_name = {}
            command.parent._slash_discordpy_adapt_name[name] = discordpy_adapt_name
        command._slash_root = root
        original_copy = command.copy

        def copy():
            c = original_copy()
            c.slash_ext = command.slash_ext
            c._slash_options = command._slash_options
            c._slash_root = command._slash_root
            c._slash_name = command._slash_name
            c._slash_description = command._slash_description
            c._slash_discordpy_adapt_name = command._slash_discordpy_adapt_name
            return c

        command.copy = copy
        return command

    return decorator


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
        for command in self.bot.walk_commands():
            if not command.hidden and hasattr(command, "slash_ext") and command.slash_ext is True:
                route = Route8("POST", f"/applications/{self.bot.user.id}/commands")
                json = {
                    "name": command._slash_name or command.name,
                    "description": command._slash_description or command.description or command._slash_name or command.name,
                    "options": [x.__dict__ for x in command._slash_options],
                }
                group = [x for x in create_requests if x["name"] == json["name"]]
                if group and group[0]:
                    group[0]["options"] += json["options"]
                else:
                    create_requests.append(json)

        raw_slash = await self.bot.http.request(Route8("GET", f"/applications/{self.bot.user.id}/commands"))
        existing = self.convert_response(raw_slash)
        expected_names = [x["name"] for x in create_requests]
        needs_update = [x for x in create_requests if x not in existing]
        needs_delete = [x for x in existing if x["name"] not in expected_names]
        print(f"existing = {existing}")
        print(f"needs_update = {needs_update}")
        print(f"needs_delete = {needs_delete}")

        for x in needs_update:
            route = Route8("POST", f"/applications/{self.bot.user.id}/commands")
            await self.bot.http.request(route, json=x)
        for x in needs_delete:
            id = next(y["id"] for y in raw_slash if y["name"] == x["name"])
            route = Route8("DELETE", f"/applications/{self.bot.user.id}/commands/{id}")
            await self.bot.http.request(route)

    def convert_response(self, raw_slash):
        return [
            {
                "name": c["name"],
                "description": c["description"],
                "options": self.convert_options(c.get("options", [])),
            }
            for c in raw_slash
        ]

    def convert_options(self, raw_options):
        return [
            {"name": o["name"], "description": o["description"], "type": o["type"], "required": o.get("required", False), "options": self.convert_options(o.get("options", []))} for o in raw_options
        ]


def patch_slash_commands(bot: Bot):
    bot._patch_slash_commands = SlashCommandPatch(bot)
    bot.add_cog(bot._patch_slash_commands)
