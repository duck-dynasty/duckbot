from .truth import Truth


async def setup(bot):
    await bot.add_cog(Truth(bot))
