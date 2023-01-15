import logging
import random

from discord import ChannelType
from discord.ext import commands, tasks
from discord.utils import get

from duckbot.util.datetime import now

from .phrases import days, templates
from .special_days import SpecialDays

log = logging.getLogger(__name__)


class AnnounceDay(commands.Cog):
    def __init__(self, bot, dog_photos):
        self.bot = bot
        self.dog_photos = dog_photos
        self.holidays = SpecialDays(bot)
        self.on_hour_loop.start()

    def cog_unload(self):
        self.on_hour_loop.cancel()

    def should_announce_day(self):
        return now().hour == 7

    def get_message(self):
        current_time = now()
        day = current_time.weekday()
        today = random.choice(days[day]["names"])
        tomorrow = random.choice(days[(day + 1) % 7]["names"])
        yesterday = random.choice(days[(day + 6) % 7]["names"])  # +6 instead of -1 since modulo can be negative
        message = random.choice(templates + days[day]["templates"]).format(today=today, tomorrow=tomorrow, yesterday=yesterday)
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
            channel = get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)
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
        day = now().weekday()
        if days[day]["gifs"]:
            await channel.send(random.choice(days[day]["gifs"]))

    @on_hour_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="day")
    async def day_command(self, context):
        await context.send(self.get_message())
