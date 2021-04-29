from discord.ext import commands


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eightball", alias="8ball")
    async def eightball_command(self, context, question: str = None):
        await self.eightball(context, question)

    async def eightball(self, context, question: str):
        pass
