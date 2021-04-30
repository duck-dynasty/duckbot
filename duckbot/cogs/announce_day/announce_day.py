import random
import datetime
import pytz
import discord
from discord import ChannelType
from discord.ext import commands, tasks
from .special_days import SpecialDays
from .phrases import days, templates


class AnnounceDay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tz = pytz.timezone("US/Eastern")
        self.holidays = SpecialDays(bot)
        self.on_hour.start()

    def cog_unload(self):
        self.on_hour.cancel()

    def should_announce_day(self):
        now = datetime.datetime.now(self.tz)
        return now.hour == 7

    def get_message(self):
        now = datetime.datetime.now(self.tz)
        day = now.weekday()
        today = random.choice(days[day]["names"])
        tomorrow = random.choice(days[(day + 1) % 7]["names"])
        message = random.choice(templates + days[day]["templates"]).format(today, tomorrow)
        if now in self.holidays:
            specials = " and ".join(self.holidays.get_list(now))
            return message + "\n" + "It is also " + specials + "."
        else:
            return message

    @tasks.loop(hours=1.0)
    async def on_hour(self):
        await self.__on_hour()

    async def __on_hour(self):
        if self.should_announce_day():
            channel = discord.utils.get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)
            if channel:
                message = self.get_message()
                await channel.send(message)

    @on_hour.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="day")
    async def day_command(self, context):
        await context.send(self.get_message())
