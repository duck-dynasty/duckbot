from .announce_day import AnnounceDay


def setup(bot):
    bot.add_cog(AnnounceDay(bot))
