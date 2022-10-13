from .aoe import AgeOfEmpires
from .coin_flip import CoinFlip
from .dice import Dice
from .discord_activity import DiscordActivity
from .office_hours import OfficeHours


async def setup(bot):
    await bot.add_cog(Dice(bot))
    await bot.add_cog(AgeOfEmpires(bot))
    await bot.add_cog(CoinFlip(bot))
    await bot.add_cog(DiscordActivity(bot))
    await bot.add_cog(OfficeHours(bot))
