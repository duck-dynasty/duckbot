from discord.ext import commands


class Tarleson(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_tarleson(self, message):
        """Corrections for tarleson"""

        if message.author == self.bot.user:
            return

        if "tucker carleson" in message.content.lower():
            correction = "I believe it is pronounced cucker tarleson"
            await message.channel.send(correction)
