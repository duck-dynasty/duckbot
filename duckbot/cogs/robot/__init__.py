from .thanking_robot import ThankingRobot


async def setup(bot):
    await bot.add_cog(ThankingRobot(bot))
