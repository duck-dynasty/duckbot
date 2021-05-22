import logging
import sys
import traceback

from discord.ext import commands


class ExceptionLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener("on_command_error")
    async def log_exceptions(self, context, exception):
        logger = logging.getLogger("discord")
        exception_string = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logger.error(exception_string)
        print("Brother, ignoring exception in command {}:".format(context.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
        
