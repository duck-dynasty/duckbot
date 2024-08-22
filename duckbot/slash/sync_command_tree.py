import logging

from discord.ext.commands import Bot, Cog

from duckbot import AppConfig

log = logging.getLogger(__name__)


class SyncCommandTree(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener("on_ready")
    async def sync_command_tree(self):
        commands = [x.to_dict(self.bot.tree) for x in self.bot.tree.get_commands()]
        log.info("registering global slash commands=%s", commands)
        await self.bot.tree.sync()

        # create only global slash commands in prod; guild commands in non-prod for quicker testing
        if not AppConfig.is_production():
            for guild in self.bot.guilds:
                log.info("registering slash commands in guild=%s commands=%s", guild.id, commands)
                await self.bot.tree.sync(guild=guild)
