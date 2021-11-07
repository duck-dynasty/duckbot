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
        bot.on_error = self.log_event_exceptions

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
    async def logs_command(self, context: commands.Context):
        await self.logs(context)

    async def logs(self, context: commands.Context):
        archive_filename = "logs.tar.gz"
        archive = tarfile.open(archive_filename, "w:gz")
        archive.add(LOGS_DIRECTORY)
        archive.close()
        log_archive = discord.File(archive_filename, archive_filename)
        await context.send(file=log_archive)

    @commands.Cog.listener("on_command_error")
    async def log_command_exceptions(self, context: commands.Context, exception):
        logger = Logging.duckbot_logger()
        trace = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logger.error(f"{self.format_function(context.command.name, context.args, context.kwargs, context.message)}\n{trace}")
        print(f"Brother, ignoring exception in command {self.format_function(context.command.name, context.args, context.kwargs)}", file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def log_event_exceptions(self, event: str, *args, **kwargs):
        logger = Logging.duckbot_logger()
        trace = traceback.format_exc()
        logger.error(f"{self.format_function(event, args, kwargs)}\n{trace}")
        print(f"Brother, ignoring exception in {self.format_function(event, args, kwargs)}", file=sys.stderr)
        traceback.print_exc()

    def format_function(self, name, args, kwargs, message=None):
        args_str = ",".join([str(a) for a in args])
        kwargs_str = ",".join([f"{k}={v}" for k, v in kwargs.items()])
        if message is None:
            message = next((x for x in args if isinstance(x, discord.Message)), None)
        message_str = f"\nmessage = {message.content}" if message else ""
        return f"{name}({args_str}, {kwargs_str}){message_str}"
