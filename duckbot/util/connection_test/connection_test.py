from discord.ext import commands

from duckbot.health import HealthCheck


class ConnectionTest(commands.Cog):
    """A listener which shuts down the bot once a valid connection has been established and sanity checks pass."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def connection_success(self):
        print("Connection Successful!")
        health = self.bot.get_cog(HealthCheck.__cog_name__)
        if health and health.sanity_check():
            print("Sanity Check Passed!")
        else:
            print("Sanity Check Failed!")
            raise RuntimeError("Sanity check failed")
        await self.bot.close()
