from .yolo_merge import YoloMerge


def setup(bot):
    bot.add_cog(YoloMerge(bot))
