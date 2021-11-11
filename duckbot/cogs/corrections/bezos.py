from discord import Message
from discord.ext import commands


class Bezos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_bezos(self, message: Message):
        """Corrections for Jeff Bezos. He is no longer the corporate overlord."""
        if message.author != self.bot.user and "bezo" in message.content.lower():
            await message.channel.send("There is no Jeff, only Andy.")
