from .wolfram_alpha import WolframAlpha


async def setup(bot):
    await bot.add_cog(WolframAlpha(bot))
