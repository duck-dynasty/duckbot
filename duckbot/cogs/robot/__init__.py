from .thanking_robot import ThankingRobot


def setup(bot):
    bot.add_cog(ThankingRobot(bot))
