from discord.ext import commands


class Shrug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shrug", description="¯\\_(ツ)_/¯")
    async def shrug_command(self, context: commands.Context):
        await self.shrug(context)

    async def shrug(self, context: commands.Context):
        await context.send("¯\\_(ツ)_/¯")
