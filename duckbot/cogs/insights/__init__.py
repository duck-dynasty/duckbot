from .insights import Insights


def setup(bot):
    bot.add_cog(Insights(bot))
