from .satisfy import Satisfy


async def setup(bot):
    await bot.add_cog(Satisfy(bot))
