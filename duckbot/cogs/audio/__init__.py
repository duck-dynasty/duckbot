from .who_can_it_be_now import WhoCanItBeNow


async def setup(bot):
    await bot.add_cog(WhoCanItBeNow(bot))
