import asyncio
import random

import discord
import requests
from discord import ChannelType, Client, TextChannel
from discord.ext import commands, tasks

from .badges import badge_symbols


class Wellness(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self._badges = {}

    @commands.hybrid_command(name="wellness", description="Add a wellness badge for the day.")
    async def wellness_command(self, context: commands.Context, *, badge: str = "poop"):
        """
        :param badge: The _thing_ done to deserve a badge for. Default is poop because you probably pooped.
        """
        await self.wellness(context, badge)

    async def wellness(self, context: commands.Context, badge):
        if badge in badge_symbols:
            if context.author.id not in self._badges:
                self._badges[context.author.id] = [badge]
            else:
                self._badges[context.author.id].append(badge)
            await context.send(f"{context.message.author.display_name} has earned the badge for {badge}.")
        else:
            await context.reply(f"One does not earn a badge for _{badge}_. " f"If you feel this should be a badge, we accept PRs, brother!", delete_after=30)

    @commands.Cog.listener("on_message")
    async def react_with_badge(self, message):
        if message.author.id in self._badges:
            await asyncio.wait([message.add_reaction(badge_symbols[badge]) for badge in self._badges[message.author.id]])

    def cog_unload(self):
        self.on_hour_loop.cancel()

    def should_clear_badges(self):
        return now().hour == 0

    @tasks.loop(hours=1.0)
    async def on_hour_loop(self):
        await self.clear_badges()

    async def clear_badges(self):
        if self.should_clear_badges():
            self._badges = {}
