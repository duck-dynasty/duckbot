import os
import tarfile

import discord
from discord.ext import commands


class GetLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duck_directory = "."
        self.log_directory = os.path.join(self.duck_directory, "logs")
        self.log_archive_path = os.path.join(self.duck_directory, "logs.tar.gz")

    @commands.command(name="logs")
    async def logs_command(self, context):
        await self.__logs(context)

    async def __logs(self, context):
        archive = tarfile.open(self.log_archive_path, "w:gz")
        archive.add(self.log_directory)
        archive.close()
        log_archive = discord.File(self.log_archive_path, "logs.tar.gz")
        await context.send(file=log_archive)
