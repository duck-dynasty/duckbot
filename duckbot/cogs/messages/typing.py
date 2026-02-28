import asyncio
import datetime
import random

import discord
from discord.ext import commands

from duckbot import DuckBot


class Typing(commands.Cog):
    def __init__(self, bot: DuckBot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_typing")
    async def typing_response(self, channel: discord.abc.Messageable, user: discord.User, when: datetime.datetime) -> None:
        """Small chance to show typing when someone starts typing."""
        if not user.bot and random.random() < 1.0 / 1_000:
            async with channel.typing():
                await asyncio.sleep(random.uniform(1.0, 3.0))
