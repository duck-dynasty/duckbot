import logging
from typing import List

from discord import Interaction
from discord.ext.commands import Bot, Cog

from .context import InteractionContext
from .slash_command import SlashCommand
from .slash_command_decorator import get_slash_command

log = logging.getLogger(__name__)


class SlashCommandHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_interaction")
    async def handle_slash_interaction(self, interaction: Interaction):
        command = next((c for c in self.bot.commands if get_slash_command(c) and c.name == interaction.data["name"]), None)
        if command:
            log.info("delegating /%s to command %s%s ; data=%s", command.name, self.bot.command_prefix, command, interaction.data)
            context = InteractionContext(bot=self.bot, interaction=interaction, command=command)
            await command.invoke(context)

    @Cog.listener("on_ready")
    async def upsert_slash_commands(self):
        slash_json = [x.to_dict() for x in self.get_commands_registered_to_bot()]
        log.info("registered slash commands=%s", slash_json)
        await self.bot.http.bulk_upsert_global_commands(self.bot.user.id, slash_json)
        for guild in self.bot.guilds:
            log.info("registering slash commands in guild=%s", guild.id)
            await self.bot.http.bulk_upsert_guild_commands(self.bot.user.id, guild.id, slash_json)

    def get_commands_registered_to_bot(self) -> List[SlashCommand]:
        slash_commands: List[SlashCommand] = []
        for command in (c for c in self.bot.walk_commands() if get_slash_command(c)):
            slash = get_slash_command(command)
            # check for a command with the same basename was already registered
            # if a command group exists, we need to merge options in order to create the top-level
            # slash command only; each @slash_command is the sub-command in those cases
            group = [x for x in slash_commands if x.name == slash.name]
            if group:
                group[0].append_options(slash.options)  # keep only the existing command to form the top-level one
            else:
                slash_commands.append(slash)
        return slash_commands
