import random
from discord.ext import commands, tasks

responses = [
    "Wow, that was insightful!",
    "That was both educational and intelligent.",
    "Wow!",
    "Thanks for sharing!",
    "You sparked my curiousity.",
]

class Insights(commands.Cog):

    def __init__(self, bot, start_tasks=True):
        self.bot = bot
        if start_tasks:
            self.check_should_respond.start()

    def cog_unload(self):
        self.check_should_respond.cancel()

    @tasks.loop(minutes=29.0)
    async def check_should_respond(self):
        await self.__check_should_respond()
    async def __check_should_respond(self):
        # get the most recent message in every channel
        # if it was dave and more than 23 minutes old
          # respond with a random response
        pass

    @check_should_respond.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
