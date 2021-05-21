import logging
import sys
import traceback

from discord.ext import commands


class ExceptionLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, context, exception):
        await self.__on_command_error(context, exception)

    async def __on_command_error(self, context, exception):
        if hasattr(context.command, "on_error"):
            return
        cog = context.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return

        logger = logging.getLogger("discord")
        exception_string = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
        logger.error(exception_string)
        print("Brother, ignoring exception in command {}:".format(context.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
