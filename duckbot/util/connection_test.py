from discord.ext import commands


class ConnectionTest(commands.Cog):
    """A listener which shuts down the bot once a valid connection has been established."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_connect")
    @commands.Cog.listener("on_ready")
    async def connection_success(self):
        print("Connection Successful!")
        await self.bot.close()
