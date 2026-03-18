import random

import discord
from discord.ext import commands

from duckbot.util.emojis import regional_indicator
from duckbot.util.messages import try_delete


class Duck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def react_duck(self, message):
        """Tiny chance to react with :duck: to any message."""
        if random.random() < 1.0 / 10_000.0:
            await message.add_reaction("\U0001f986")
            await self.post_to_duckboard(message)

    async def post_to_duckboard(self, message):
        """Post a duck reaction announcement to the #duckboard channel."""
        if message.guild is not None:
            duckboard = discord.utils.get(message.guild.text_channels, name="duckboard")
            if duckboard is not None:
                embed = discord.Embed(description=message.content, color=0xF4AC0B, url=message.jump_url)
                embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="\u200b", value=message.channel.mention)
                await duckboard.send(embed=embed)

    @commands.Cog.listener("on_message")
    async def react_with_duckbot(self, message):
        """Chance to react with "I AM DUCKBOT" to the bot's own messages."""
        if self.bot.user == message.author and random.random() < 1.0 / 100.0:
            for c in "iamduckbot":
                await message.add_reaction(regional_indicator(c))

    @commands.command(name="duck")
    async def duck_command(self, context):
        await self.github(context)

    async def github(self, context):
        await context.send("https://github.com/duck-dynasty/duckbot")

    @commands.command(name="help", aliases=["wiki"])
    async def wiki_command(self, context):
        await self.wiki(context)

    async def wiki(self, context):
        await context.send("https://github.com/duck-dynasty/duckbot/wiki")

    @duck_command.after_invoke
    @wiki_command.after_invoke
    async def delete_command_message(self, context):
        await try_delete(context.message)
