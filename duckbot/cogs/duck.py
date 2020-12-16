from discord.ext import commands
import random

class Duck(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener('on_message')
    async def react_duck(self, message):
        """Tiny chance to react with :duck: to any message."""
        if random.random() < 1.0 / 10_000.0:
            await message.add_reaction("\U0001F986")
