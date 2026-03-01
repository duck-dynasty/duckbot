from .bezos import Bezos
from .bitcoin import Bitcoin
from .kubernetes import Kubernetes
from .tarlson import Tarlson
from .typos import Typos


async def setup(bot):
    await bot.add_cog(Bitcoin())
    await bot.add_cog(Kubernetes(bot))
    await bot.add_cog(Typos())
    await bot.add_cog(Bezos())
    await bot.add_cog(Tarlson())
