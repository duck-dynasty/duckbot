from .edit_diff import EditDiff
from .haiku import Haiku
from .touch_grass import TouchGrass
from .typing import Typing


async def setup(bot):
    await bot.add_cog(EditDiff())
    await bot.add_cog(Haiku(bot))
    await bot.add_cog(TouchGrass(bot))
    await bot.add_cog(Typing(bot))
