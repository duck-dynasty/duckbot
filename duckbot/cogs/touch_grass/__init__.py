from .touch_grass import TouchGrass


async def setup(bot):
    await bot.add_cog(TouchGrass(bot))
