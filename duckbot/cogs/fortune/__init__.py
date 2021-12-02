from .eightball import EightBall
from .fortune import Fortune
from .stocks import Stocks


def setup(bot):
    bot.add_cog(Fortune(bot))
    bot.add_cog(EightBall(bot))
    bot.add_cog(Stocks(bot))
