from .duck import Duck


def setup(bot):
    bot.add_cog(Duck(bot))
