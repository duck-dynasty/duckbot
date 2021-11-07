from .logging import Logging


def setup(bot):
    Logging.define_logs()
    bot.add_cog(Logging(bot))
