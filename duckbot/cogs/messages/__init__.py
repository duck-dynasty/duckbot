from .edit_diff import EditDiff
from .haiku import Haiku
from .typing import Typing


async def setup(bot):
    await bot.add_cog(EditDiff(bot))
    await bot.add_cog(Haiku(bot))
    await bot.add_cog(Typing(bot))
