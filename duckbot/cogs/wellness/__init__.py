from .wellness import Wellness


async def setup(bot):
    await bot.add_cog(Wellness(bot))
