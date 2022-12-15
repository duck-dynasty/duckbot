from .tito import Tito


async def setup(bot):
    await bot.add_cog(Tito(bot))
