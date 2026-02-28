from .eightball import EightBall
from .fortune import Fortune
from .stocks import Stocks


async def setup(bot):
    await bot.add_cog(Fortune())
    await bot.add_cog(EightBall())
    await bot.add_cog(Stocks())
