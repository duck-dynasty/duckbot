from .aoe import AgeOfEmpires
from .coin_flip import CoinFlip
from .dice import Dice


def setup(bot):
    bot.add_cog(Dice(bot))
    bot.add_cog(AgeOfEmpires(bot))
    bot.add_cog(CoinFlip(bot))
