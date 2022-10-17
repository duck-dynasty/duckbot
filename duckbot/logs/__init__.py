from .logging import Logging, loop_replacement


async def setup(bot):
    await bot.add_cog(Logging(bot))
