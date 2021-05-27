import logging

from discord.ext.commands import Bot, Cog

from .context import InteractionContext
from .interaction import Interaction
from .route import Route8

log = logging.getLogger(__name__)


class SlashCommandPatch(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        # patch handler for discord slash command events
        bot._connection.parsers["INTERACTION_CREATE"] = self.parse_interaction_create

    def parse_interaction_create(self, data):
        interaction = Interaction(bot=self.bot, data=data)
        self.bot.dispatch("slash", interaction)  # creates `on_slash` bot event

    @Cog.listener("on_slash")
    async def handle_slash_interaction(self, interaction: Interaction):
        for command in self.bot.commands:
            # slash_ext is patched in @slash_command
            if hasattr(command, "slash_ext") and command.slash_ext and command.name == interaction.data["name"]:
                log.info("delegating /%s to command %s", command.name, command)
                context = InteractionContext(bot=self.bot, interaction=interaction, command=command)
                await command.invoke(context)
                return

    @Cog.listener("on_ready")
    async def register_commands(self):
        create_requests = self.get_registered_slash_commands()

        raw_slash = await self.bot.http.request(Route8("GET", f"/applications/{self.bot.user.id}/commands"))
        existing = self.convert_response(raw_slash)
        expected_names = [x["name"] for x in create_requests]
        needs_update = [x for x in create_requests if x not in existing]
        needs_delete = [x for x in existing if x["name"] not in expected_names]
        log.debug("slash commands existing = %s  ;  expected = %s", raw_slash, create_requests)

        for x in needs_update:
            log.info("updating slash command %s ; data=%s", x["name"], x)
            route = Route8("POST", f"/applications/{self.bot.user.id}/commands")
            await self.bot.http.request(route, json=x)
        for x in needs_delete:
            log.info("deleting slash command %s ; data=%s", x["name"], x)
            slash_id = next(y["id"] for y in raw_slash if y["name"] == x["name"])
            route = Route8("DELETE", f"/applications/{self.bot.user.id}/commands/{slash_id}")
            await self.bot.http.request(route)

    def get_registered_slash_commands(self):
        create_requests = []
        for command in self.bot.walk_commands():
            if hasattr(command, "slash_ext") and command.slash_ext:
                json = {
                    "name": command.slash_ext.name,
                    "description": command.slash_ext.description,
                    "options": [x.to_dict() for x in command.slash_ext.options],
                }
                group = [x for x in create_requests if x["name"] == json["name"]]
                if group and group[0]:  # if a command with the same basename was already registered
                    group[0]["options"] += json["options"]  # append the options, for sub-command registration
                else:
                    create_requests.append(json)
        return create_requests

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
