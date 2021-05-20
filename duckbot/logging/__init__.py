from .get_logs import GetLogs


def setup(bot):
    bot.add_cog(GetLogs(bot))
