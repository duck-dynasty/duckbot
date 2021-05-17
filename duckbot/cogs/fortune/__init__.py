from .eightball import EightBall
from .fortune import Fortune


def setup(bot):
    bot.add_cog(Fortune(bot))
    bot.add_cog(EightBall(bot))
