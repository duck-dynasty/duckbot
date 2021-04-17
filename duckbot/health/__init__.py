from .health_check import HealthCheck


def setup(bot):
    bot.add_cog(HealthCheck(bot))
