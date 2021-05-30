from .ascii import Ascii


def setup(bot):
    bot.add_cog(Ascii(bot))
