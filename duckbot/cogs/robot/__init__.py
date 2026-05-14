from .thanking_robot import ThankingRobot
from .thanks_reactor import ThanksReactor


async def setup(bot):
    await bot.add_cog(ThankingRobot())
    await bot.add_cog(ThanksReactor(bot))
