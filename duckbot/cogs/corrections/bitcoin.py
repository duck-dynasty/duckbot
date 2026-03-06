import discord
from discord.ext import commands


class Bitcoin(commands.Cog):
    @commands.Cog.listener("on_message")
    async def correct_bitcoin(self, message):
        """Corrections for bitcoin"""

        if message.author.bot:
            return

        if "bitcoin" in discord.utils.remove_markdown(message.clean_content).lower():
            correction = "Magic Beans*"
            await message.channel.send(correction)
