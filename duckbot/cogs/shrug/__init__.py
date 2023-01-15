from .shrug import Shrug


async def setup(bot):
    await bot.add_cog(Shrug(bot))
