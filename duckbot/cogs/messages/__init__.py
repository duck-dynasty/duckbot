from .edit_diff import EditDiff
from .haiku import Haiku


def setup(bot):
    bot.add_cog(EditDiff(bot))
    bot.add_cog(Haiku(bot))
