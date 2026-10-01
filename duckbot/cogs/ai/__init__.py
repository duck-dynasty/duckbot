from .explain import Explain
from .truth import Truth


async def setup(bot):
    await bot.add_cog(Truth())
    await bot.add_cog(Explain())
