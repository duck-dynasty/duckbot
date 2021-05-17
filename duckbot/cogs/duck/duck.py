import random

from discord.ext import commands

from duckbot.util.emojis import regional_indicator


class Duck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def react_duck(self, message):
        """Tiny chance to react with :duck: to any message."""
        if random.random() < 1.0 / 10_000.0:
            await message.add_reaction("\U0001F986")

    @commands.Cog.listener("on_message")
    async def react_with_duckbot(self, message):
        """Chance to react with "I AM DUCKBOT" to the bot's own messages."""
        if self.bot.user == message.author and random.random() < 1.0 / 100.0:
            for c in "iamduckbot":
                await message.add_reaction(regional_indicator(c))

    @commands.command(name="duck")
    async def github(self, context):
        await self.__github(context)

    async def __github(self, context):
        await context.send("https://github.com/Chippers255/duckbot")

    @commands.command(name="help")
    async def wiki(self, context):
        await self.__wiki(context)

    async def __wiki(self, context):
        await context.send("https://github.com/Chippers255/duckbot/wiki")
