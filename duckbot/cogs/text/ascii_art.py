import pyfiglet
from discord.ext import commands


class AsciiArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ascii")
    async def ascii_command(self, context, *, text: str = "I need text, brother."):
        await self.ascii(context, text)

    async def ascii(self, context, text: str):
        art = str(pyfiglet.figlet_format(text.strip()))
        if len(art) < 1990:
            await context.send(f"```{art}```")
        else:
            art = str(pyfiglet.figlet_format("Happy Birthday!"))
            await context.send(f"Discord won't let me send art with that much GUSTO, so here's a happy birthday.\n```{art}```")
