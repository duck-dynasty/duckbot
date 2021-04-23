from .edit_diff import EditDiff


def setup(bot):
    bot.add_cog(EditDiff(bot))
