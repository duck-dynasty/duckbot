from .fortune import Fortune


def setup(bot):
    bot.add_cog(Fortune(bot))
