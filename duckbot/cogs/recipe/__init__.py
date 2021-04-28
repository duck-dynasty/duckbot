from .recipe import Recipe


def setup(bot):
    bot.add_cog(Recipe(bot))
