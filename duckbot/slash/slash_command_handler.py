import logging

from discord import Interaction
from discord.ext.commands import Bot, Cog

from .context import InteractionContext
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
