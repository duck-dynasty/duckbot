import tarfile

import discord
from discord.ext import commands


class GetLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_directory = "logs"
        self.log_archive_name = "logs.tar.gz"

    @commands.command(name="logs")
    async def logs_command(self, context):
        await self.logs(context)

    async def logs(self, context):
        archive = tarfile.open(self.log_archive_name, "w:gz")
        archive.add(self.log_directory)
        archive.close()
        log_archive = discord.File(self.log_archive_name, "logs.tar.gz")
        await context.send(file=log_archive)
