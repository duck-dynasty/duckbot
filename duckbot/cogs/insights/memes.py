import datetime
import random
from typing import Optional

from discord import ChannelType, Client, TextChannel
from discord.ext import commands
from discord.utils import get, utcnow


class Memes(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    @commands.hybrid_command(name="meme", description="Show a random meme from the memes channel")
    async def meme(self, context: commands.Context):
        channel = self.get_memes_channel()
        url = await self.find_meme(channel) if channel else None
        await context.send(url if url else "https://tenor.com/view/gnocchi-soup-gif-27425983")

    async def find_meme(self, channel: TextChannel) -> Optional[str]:
        for _ in range(5):
            url = await self.random_attachment(channel)
            if url:
                return url
        return None

    def get_memes_channel(self) -> Optional[TextChannel]:
        return get(self.bot.get_all_channels(), guild__name="Friends Chat", name="toms-memes", type=ChannelType.text)

    async def random_attachment(self, channel: TextChannel) -> Optional[str]:
        messages = [msg async for msg in channel.history(limit=100, around=self.random_time(channel))]  # discord caps `around` at 101
        memes = [msg for msg in messages if msg.attachments]
        return random.choice(random.choice(memes).attachments).url if memes else None

    def random_time(self, channel: TextChannel) -> datetime.datetime:
        seconds = (utcnow() - channel.created_at).total_seconds()
        return channel.created_at + datetime.timedelta(seconds=random.uniform(0, seconds))
