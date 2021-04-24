from .tito import Tito


def setup(bot):
    bot.add_cog(Tito(bot))
