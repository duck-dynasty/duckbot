import discord
from discord.ext import commands
import os
import subprocess


class GetLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # TODO Verify the paths are setup correctly
        self.duck_dir = os.getcwd()
        self.log_dir = os.path.join(self.duck_dir, "logs")
        self.log_archive_path = os.path.join(self.duck_dir, "logs.tar.gz")
        self.compress_command = ["tar", "-zc", "-f", self.log_archive_path, self.log_dir]

    @commands.command(name="logs")
    async def logs_command(self, context):
        await self.__logs(context)

    async def __logs(self, context):
        await subprocess.call(self.compress_command)
        log_archive = await discord.File(self.log_archive_path, "duck.logs")
        await context.send(file=log_archive)
        # await subprocess.call(["rm", self.log_archive_path])
