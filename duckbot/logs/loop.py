import sys
import traceback

import discord.ext.tasks

from duckbot.logs import Logging

discordpy_loop = discord.ext.tasks.loop


def loop_replacement(*args, **kwargs):
    """The monkeypatch replacement for discord.ext.tasks.loop. This behaves identically, but produces a loop with an @error method to log any exceptions.
    The actual monkeypatch is applied in the top level __init__.py"""

    def decorator(func):
        loop = discordpy_loop(*args, **kwargs)(func)

        @loop.error
        async def log_error(*error_args):
            exception = error_args[-1]
            logger = Logging.duckbot_logger()
            trace = "".join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
            logger.error(f"{loop.coro.__name__}\n{trace}")
            print(f"Brother, ignoring exception in task {loop.coro.__name__}", file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)

        return loop

    return decorator
