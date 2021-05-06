from .dog_photos import DogPhotos


def setup(bot):
    bot.add_cog(DogPhotos(bot))
