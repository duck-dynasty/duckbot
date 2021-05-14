from .dice import Dice
from .aoe import AgeOfEmpires


def setup(bot):
    bot.add_cog(Dice(bot))
    bot.add_cog(AgeOfEmpires(bot))
