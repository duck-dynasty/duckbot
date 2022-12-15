from .bezos import Bezos
from .bitcoin import Bitcoin
from .kubernetes import Kubernetes
from .tarlson import Tarlson
from .typos import Typos


async def setup(bot):
    await bot.add_cog(Bitcoin(bot))
    await bot.add_cog(Kubernetes(bot))
    await bot.add_cog(Typos(bot))
    await bot.add_cog(Bezos(bot))
    await bot.add_cog(Tarlson(bot))
