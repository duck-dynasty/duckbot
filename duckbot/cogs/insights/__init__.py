from .insights import Insights


async def setup(bot):
    await bot.add_cog(Insights(bot))
