from .fortune import Fortune
from .eightball import EightBall


def setup(bot):
    bot.add_cog(Fortune(bot))
    bot.add_cog(EightBall(bot))
