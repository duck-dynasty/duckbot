from .recipe import Recipe


async def setup(bot):
    await bot.add_cog(Recipe(bot))
