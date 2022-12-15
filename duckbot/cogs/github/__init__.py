from .yolo_merge import YoloMerge


async def setup(bot):
    await bot.add_cog(YoloMerge(bot))
