from .announce_day import AnnounceDay


def setup(bot):
    from duckbot.cogs.dogs import DogPhotos

    bot.add_cog(AnnounceDay(bot, DogPhotos(bot)))
