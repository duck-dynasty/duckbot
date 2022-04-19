from .bezos import Bezos
from .bitcoin import Bitcoin
from .kubernetes import Kubernetes
from .tarlson import Tarlson
from .typos import Typos


def setup(bot):
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(Typos(bot))
    bot.add_cog(Bezos(bot))
    bot.add_cog(Tarlson(bot))
