from discord.ext import commands


class Ascii(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ascii")
    async def ascii_command(self, context, *, text: str = None):
        await self.ascii(context, text)

    async def ascii(self, context, text: str):
        pass
