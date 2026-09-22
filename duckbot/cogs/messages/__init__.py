from .edit_diff import EditDiff
from .emoji_usage import EmojiUsage
from .friend_facts import FriendFacts
from .haiku import Haiku
from .touch_grass import TouchGrass
from .typing import Typing


async def setup(bot):
    await bot.add_cog(EditDiff())
    await bot.add_cog(EmojiUsage())
    await bot.add_cog(FriendFacts(bot))
    await bot.add_cog(Haiku())
    await bot.add_cog(TouchGrass(bot))
    await bot.add_cog(Typing(bot))
