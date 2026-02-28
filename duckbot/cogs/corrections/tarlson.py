from discord.ext import commands


class Tarlson(commands.Cog):
    @commands.Cog.listener("on_message")
    async def correct_tarlson(self, message):
        """Corrections for tarlson"""

        if message.author.bot:
            return

        if "tucker carlson" in message.content.lower():
            correction = "I believe it is pronounced cucker tarlson"
            await message.channel.send(correction)
