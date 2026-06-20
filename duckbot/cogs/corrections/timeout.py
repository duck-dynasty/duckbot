import asyncio
import datetime

import discord
from discord import Message
from discord.ext import commands

from duckbot import DuckBot

YELLING_THRESHOLD = 0.8  # 80% caps = yelling
TIMEOUT_SECONDS = 300  # 5 minutes


class Timeout(commands.Cog):
    def __init__(self, bot: DuckBot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def timeout_yellers(self, message: Message) -> None:
        """Give people a timeout for yelling too much."""
        if not message.author.bot and isinstance(message.author, discord.Member) and self.is_yelling(message.content):
            await message.reply(f"That's too many yelling, {message.author.display_name}. Have a five minute timeout.")
            await message.author.timeout(datetime.timedelta(seconds=TIMEOUT_SECONDS))
            await asyncio.sleep(TIMEOUT_SECONDS)
            await message.channel.send(f"Welcome back {message.author.display_name}! I hope you are more civil now.")

    def is_yelling(self, content: str) -> bool:
        """Returns True if the message is mostly uppercase."""
        letters = [c for c in content if c.isalpha()]
        if len(letters) < 5:
            return False
        return sum(1 for c in letters if c.isupper()) / len(letters) >= YELLING_THRESHOLD