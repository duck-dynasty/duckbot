from .health_check import HealthCheck


async def setup(bot):
    await bot.add_cog(HealthCheck(bot))
