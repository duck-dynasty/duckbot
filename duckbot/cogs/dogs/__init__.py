from .dog_photos import DogPhotos


async def setup(bot):
    await bot.add_cog(DogPhotos(bot))
