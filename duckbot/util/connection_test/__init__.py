from .connection_test import ConnectionTest


def setup(bot):
    bot.add_cog(ConnectionTest(bot))
