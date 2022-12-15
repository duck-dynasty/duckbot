from .eightball import EightBall
from .fortune import Fortune
from .stocks import Stocks


async def setup(bot):
    await bot.add_cog(Fortune(bot))
    await bot.add_cog(EightBall(bot))
    await bot.add_cog(Stocks(bot))
