import random

import discord
from discord.ext import commands

from .phrases import phrases


class FormulaOne(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supermax = None
        self.phrases = [""]

    @commands.Cog.listener("on_ready")
    async def store_emojis(self):
        self.supermax = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="supermax")
        self.phrases = phrases(self.supermax)

    @commands.Cog.listener("on_message")
    async def car_do_be_going_fast_though(self, message):
        if self.is_dank_channel(message.channel):
            for letter in random.choice(self.phrases):
                await message.add_reaction(letter)

    def is_dank_channel(self, channel):
        return hasattr(channel, "name") and channel.name == "dank"
