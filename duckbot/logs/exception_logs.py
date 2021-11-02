import logging
import sys
import traceback

from discord.ext import commands


class ExceptionLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.on_error = self.log_error

    @commands.Cog.listener("on_command_error")
    async def log_exceptions(self, context: commands.Context, exception):
        logger = logging.getLogger("duckbot")
        exception_string = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logger.error(f"{self.format_function(context.command.name, context.args, context.kwargs)}\n{exception_string}")
        print(f"Brother, ignoring exception in command {context.command}:", file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

    async def log_error(self, event: str, *args, **kwargs):
        logger = logging.getLogger("duckbot")
        trace = traceback.format_exc()
        args_str = ",".join([str(a) for a in args])
        kwargs_str = ",".join([f"{k}={v}" for k, v in kwargs.items()])
        logger.error(f"{event}({args_str}, {kwargs_str}\n{trace}")
        print(f'Brother, ignoring exception in {event}', file=sys.stderr)
        traceback.print_exc()

    def format_function(self, name, args, kwargs):
        args_str = ",".join([str(a) for a in args])
        kwargs_str = ",".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"{name}({args_str}, {kwargs_str}"
