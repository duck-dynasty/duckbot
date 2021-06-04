import random

from discord.ext import commands


class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coin", aliases=["flip", "toss"])
    async def coin_command(self, context):
        await self.coin_flip(context)

    async def coin_flip(self, context):
        faces = ["Heads!", "Tails"] * 50 + ["The Side"]
        await context.send(f":coin: :coin: {random.choice(faces)} :coin: :coin:")
