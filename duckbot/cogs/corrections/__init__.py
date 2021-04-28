from .bitcoin import Bitcoin
from .kubernetes import Kubernetes
from .typos import Typos


def setup(bot):
    bot.add_cog(Bitcoin(bot))
    bot.add_cog(Kubernetes(bot))
    bot.add_cog(Typos(bot))
