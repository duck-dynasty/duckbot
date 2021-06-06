import pyfiglet
from discord.ext import commands

from duckbot.util.messages import MAX_MESSAGE_LENGTH


class AsciiArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ascii")
    async def ascii_command(self, context, *, text: str = "I need text, brother."):
        await self.ascii(context, text)

    async def ascii(self, context, text: str):
        art = str(pyfiglet.figlet_format(text.strip()))
        if len(art) < MAX_MESSAGE_LENGTH - 6:  # max-6 for the ``` characters
            await context.send(f"```{art}```")
        else:
            art = str(pyfiglet.figlet_format("Happy Birthday!"))
            await context.send(f"Discord won't let me send art with that much GUSTO, so here's a happy birthday.\n```{art}```")
