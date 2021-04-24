from discord.ext import commands


class ThankingRobot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_giving_thanks(self, message):
        """Correcting people who thank the robot"""

        if message.author == self.bot.user:
            return

        thanks = ["thank you duckbot", "thanks duckbot", "thank you duck bot", "thanks duck bot"]
        for t in thanks:
            if t in message.content.lower().replace(",", ""):
                author = str(message.author).split("#")[0]
                correction = f"I am just a robot.  Do not personify me, {author}"
                await message.channel.send(correction)
