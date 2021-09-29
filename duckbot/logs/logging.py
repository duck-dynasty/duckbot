import logging
import logging.handlers
import os
import sys
import tarfile
import traceback

import discord
from discord.ext import commands

LOGS_DIRECTORY = "logs"


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def define_logs(cls):
        os.makedirs(LOGS_DIRECTORY, exist_ok=True)

        handler = logging.handlers.RotatingFileHandler(filename=os.path.join(LOGS_DIRECTORY, "duck.log"), mode="a", maxBytes=256000, backupCount=10)
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

        discord = Logging.discord_logger()
        discord.setLevel(logging.INFO)
        discord.addHandler(handler)

        duckbot = Logging.duckbot_logger()
        duckbot.setLevel(logging.INFO)
        duckbot.addHandler(handler)

    @classmethod
    def discord_logger(cls):
        return logging.getLogger("discord")

    @classmethod
    def duckbot_logger(cls):
        return logging.getLogger("duckbot")

    @commands.command(name="logs")
    async def logs_command(self, context):
        await self.logs(context)

    async def logs(self, context):
        archive_filename = "logs.tar.gz"
        archive = tarfile.open(archive_filename, "w:gz")
        archive.add(LOGS_DIRECTORY)
        archive.close()
        log_archive = discord.File(archive_filename, archive_filename)
        await context.send(file=log_archive)

    @commands.Cog.listener("on_command_error")
    async def log_exceptions(self, context, exception):
        logger = Logging.discord_logger()
        exception_string = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logger.error(exception_string)
        print(f"Brother, ignoring exception in command {context.command}:", file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
