import random
import datetime
import server.channels as channels
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

    @tasks.loop(minutes=139.0)
    async def check_should_respond(self):
        await self.__check_should_respond()

    async def __check_should_respond(self):
        channel = self.bot.get_channel(channels.GENERAL)
        message = await self.__get_last_message(channel)
        if self.should_respond(message):
            response = random.choice(responses)
            await channel.send(response)

    async def __get_last_message(self, channel):
        message = await channel.history(limit=1).flatten()
        if message:
            return message[0]
        else:
            return None

    def should_respond(self, message):
        stamp = datetime.datetime.utcnow() - datetime.timedelta(minutes=23)
        return message is not None and stamp >= message.created_at and message.author.id == 244629273191645184

    @check_should_respond.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
