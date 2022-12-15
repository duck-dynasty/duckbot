from .edit_diff import EditDiff
from .haiku import Haiku


async def setup(bot):
    await bot.add_cog(EditDiff(bot))
    await bot.add_cog(Haiku(bot))
