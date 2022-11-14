import random

from discord.ext import commands


class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coin", aliases=["flip", "toss"])
    async def coin_command(self, context):
        await self.coin_flip(context)

    async def coin_flip(self, context):
        if random.random() < 1.0 / 6_000.0:
            await context.send(":coin: :coin: The Side! :coin: :coin:")
            await context.send("1v1 me bro: https://journals.aps.org/pre/abstract/10.1103/PhysRevE.48.2547")
        else:
            await context.send(f":coin: :coin: {random.choice(['Heads!', 'Tails!'])} :coin: :coin:")
