import logging
import logging.handlers
import os
import tarfile
import traceback

import discord
import discord.ext.tasks
from discord.ext import commands

# store the original loop function so we can delegate to it
discordpy_loop = discord.ext.tasks.loop

LOGS_DIRECTORY = "logs"


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.on_error = self.log_event_exceptions

    @classmethod
    def define_logs(cls):
        os.makedirs(LOGS_DIRECTORY, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
            handlers=[
                logging.handlers.RotatingFileHandler(filename=os.path.join(LOGS_DIRECTORY, "duck.log"), mode="a", maxBytes=256000, backupCount=10),
                logging.StreamHandler(),  # logs to stderr
            ],
        )

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
        name = context.cog.__module__ if context.cog else context.bot.__module__
        trace = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logging.getLogger(name).error(f"{self.format_function(context.command.name, context.args, context.kwargs, context.message)}\n{trace}")

    async def log_event_exceptions(self, event: str, *args, **kwargs):
        trace = traceback.format_exc()
        logging.getLogger("duckbot").error(f"{self.format_function(event, args, kwargs)}\n{trace}")

    def format_function(self, name, args, kwargs, message=None):
        args_str = ",".join([str(a) for a in args])
        kwargs_str = ",".join([f"{k}={v}" for k, v in kwargs.items()])
        if message is None:
            message = next((x for x in args if isinstance(x, discord.Message)), None)
        message_str = f"\nmessage = {message.content}" if message else ""
        return f"{name}({args_str}, {kwargs_str}){message_str}"


def loop_replacement(*args, **kwargs):
    """The monkeypatch replacement for discord.ext.tasks.loop. This behaves identically, but produces a loop with an @error method to log any exceptions.
    The actual monkeypatch is applied in the top level __init__.py"""

    def decorator(func):
        loop = discordpy_loop(*args, **kwargs)(func)

        @loop.error
        async def log_error(*error_args):
            bot_self = error_args[0]  # may be the same as exception, but is typically the `self` parameter in the method, ie the cog/bot instance
            exception = error_args[-1]
            name = "duckbot" if bot_self == exception else bot_self.__module__
            trace = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
            logging.getLogger(name).error(f"{loop.coro.__name__}\n{trace}")

        return loop

    return decorator
