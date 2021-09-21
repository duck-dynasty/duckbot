import random

from discord.ext import commands

from .phrases import phrases


class FormulaOne(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def car_do_be_going_fast_though(self, message):
        if self.is_dank_channel(message.channel):
            for letter in random.choice(phrases):
                await message.add_reaction(letter)

    def is_dank_channel(self, channel):
        return hasattr(channel, "name") and channel.name == "dank"
