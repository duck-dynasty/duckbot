import logging
import random
from datetime import time
from importlib.resources import path

from discord import ChannelType, File
from discord.ext import commands, tasks
from discord.utils import get

import duckbot.util.datetime

from .phrases import days, templates
from .special_days import SpecialDays

log = logging.getLogger(__name__)


class AnnounceDay(commands.Cog):
    def __init__(self, bot, dog_photos, days=days, templates=templates):
        self.bot = bot
        self.dog_photos = dog_photos
        self.holidays = SpecialDays(bot)
        self.days = days
        self.templates = templates
        self.on_hour_loop.start()
        self.on_gandalf_loop.start()

    def cog_unload(self):
        self.on_hour_loop.cancel()
        self.on_gandalf_loop.cancel()

    def get_general_channel(self):
        return get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)

    def should_announce_day(self):
        return duckbot.util.datetime.now().hour == 7

    def get_message(self):
        current_time = duckbot.util.datetime.now()
        day = current_time.weekday()
        today = random.choice(self.days[day]["names"])
        tomorrow = random.choice(self.days[(day + 1) % 7]["names"])
        yesterday = random.choice(self.days[(day + 6) % 7]["names"])  # +6 instead of -1 since modulo can be negative
        message = random.choice(self.templates + self.days[day]["templates"]).format(today=today, tomorrow=tomorrow, yesterday=yesterday)
        if current_time in self.holidays:
            specials = " and ".join(self.holidays.get_list(current_time))
            return message + "\n" + "It is also " + specials + "."
        else:
            return message

    @tasks.loop(hours=1.0)
    async def on_hour_loop(self):
        await self.on_hour()

    async def on_hour(self):
        if self.should_announce_day():
            channel = self.get_general_channel()
            message = self.get_message()
            await channel.send(message)

            should_send_dog = random.random() < 1.0 / 10.0
            should_send_gif = not should_send_dog and random.random() < 1.0 / 9.0  # 10%, since relies on not sending dog photo
            await self.send_dog(channel) if should_send_dog else None
            await self.send_gif(channel) if should_send_gif else None

    async def send_dog(self, channel):
        try:
            dogs = [":dog:", ":dog2:", ":guide_dog:", ":service_dog:", ":hotdog:", ":feet:", ":bone:"]
            await channel.send(f"Also, here's a dog! {random.choice(dogs)}\n{self.dog_photos.get_dog_image()}")
        except Exception as e:
            log.warning(e, exc_info=True)  # ignore failures for sending dog photo

    async def send_gif(self, channel):
        day = duckbot.util.datetime.now().weekday()
        if self.days[day]["gifs"]:
            await channel.send(random.choice(self.days[day]["gifs"]))

    @commands.command(name="day")
    async def day_command(self, context):
        await context.send(self.get_message())

    @tasks.loop(time=time(hour=10, minute=0, tzinfo=duckbot.util.datetime.timezone()))
    async def on_gandalf_loop(self):
        await self.on_gandalf()

    async def on_gandalf(self):
        channel = self.get_general_channel()
        with path("resources", "10am-mfer.png") as img:
            gandalf = File(str(img))
            await channel.send(file=gandalf)

    @on_hour_loop.before_loop
    @on_gandalf_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
