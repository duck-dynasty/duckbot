from .duck import Duck


async def setup(bot):
    await bot.add_cog(Duck(bot))
