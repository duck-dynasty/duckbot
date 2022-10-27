from .connection_test import ConnectionTest


async def setup(bot):
    await bot.add_cog(ConnectionTest(bot))
