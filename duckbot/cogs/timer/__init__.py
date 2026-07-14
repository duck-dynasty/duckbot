from .timer import Timer


async def setup(bot):
    await bot.add_cog(Timer())
