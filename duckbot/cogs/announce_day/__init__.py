from .announce_day import AnnounceDay


async def setup(bot):
    from duckbot.cogs.dogs import DogPhotos

    await bot.add_cog(AnnounceDay(bot, DogPhotos(bot)))
