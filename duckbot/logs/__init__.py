from .logging import Logging, loop_replacement


def setup(bot):
    Logging.define_logs()
    bot.add_cog(Logging(bot))
