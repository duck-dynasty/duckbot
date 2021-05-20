from .aoe import AgeOfEmpires
from .dice import Dice


def setup(bot):
    bot.add_cog(Dice(bot))
    bot.add_cog(AgeOfEmpires(bot))
