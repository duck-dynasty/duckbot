import datetime
import random

from discord import ChannelType
from discord.ext import commands, tasks
from discord.utils import get, utcnow

from .phrases import responses


class Insights(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_should_respond_loop.start()

    def cog_unload(self):
        self.check_should_respond_loop.cancel()

    @tasks.loop(minutes=139.0)
    async def check_should_respond_loop(self):
        await self.check_should_respond()

    async def check_should_respond(self):
        channel = get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)
        message = await self.__get_last_message(channel)
        if self.should_respond(message):
            response = random.choice(responses)
            await channel.send(response)

    async def __get_last_message(self, channel):
        message = await channel.history(limit=1).flatten() if channel is not None else None
        if message:
            return message[0]
        else:
            return None

    def should_respond(self, message):
        stamp = utcnow() - datetime.timedelta(minutes=23)
        return message is not None and stamp >= message.created_at and message.author.id == 244629273191645184

    @check_should_respond_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="insight")
    async def insight_command(self, context):
        await self.insight(context)

    async def insight(self, context):
        await context.send(random.choice(responses))
