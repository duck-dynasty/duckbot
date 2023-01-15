import logging
import random

from discord import ChannelType
from discord.ext import commands, tasks
from discord.utils import get

class Shrug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shrug")
    async def day_command(self, context):
        await context.send("¯\_(ツ)_/¯")