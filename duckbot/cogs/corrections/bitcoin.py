from discord.ext import commands


class Bitcoin(commands.Cog):
    @commands.Cog.listener("on_message")
    async def correct_bitcoin(self, message):
        """Corrections for bitcoin"""

        if message.author.bot:
            return

        if "bitcoin" in message.content.lower():
            correction = "Magic Beans*"
            await message.channel.send(correction)
