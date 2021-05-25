from .define_logs import define_logs
from .exception_logs import ExceptionLogs
from .get_logs import GetLogs


def setup(bot):
    bot.add_cog(ExceptionLogs(bot))
    bot.add_cog(GetLogs(bot))
