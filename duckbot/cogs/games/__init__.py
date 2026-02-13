from .aoe import AgeOfEmpires
from .coin_flip import CoinFlip
from .dice import Dice
from .discord_activity import DiscordActivity
from .office_hours import OfficeHours
from .pokemon import Pokemon
from .satisfy import setup as satisfy_setup


async def setup(bot):
    await bot.add_cog(Dice(bot))
    await bot.add_cog(AgeOfEmpires(bot))
    await bot.add_cog(CoinFlip(bot))
    await bot.add_cog(DiscordActivity(bot))
    await bot.add_cog(OfficeHours(bot))
    await bot.add_cog(Pokemon(bot))
    await satisfy_setup(bot)
