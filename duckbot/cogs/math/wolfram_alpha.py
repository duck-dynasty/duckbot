import itertools
import os
import urllib.parse

import discord
import wolframalpha
from discord.ext import commands


class WolframAlpha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._wolfram = None

    @property
    def wolfram(self):
        if self._wolfram is None:
            self._wolfram = wolframalpha.Client(os.getenv("WOLFRAM_ALPHA_TOKEN"))
        return self._wolfram

    @commands.command(name="calc")
    async def calc_command(self, context: commands.Context, *, query: str = "the answer to the ultimate question of life, the universe, and everything"):
        async with context.typing():
            await self.calc(context, query)

    async def calc(self, context: commands.Context, query: str):
        result = self.wolfram.query(query)
        embeds = [self.as_embed(pod) for pod in itertools.islice(result.pods, 5)]
        await context.send(f"https://www.wolframalpha.com/input/?i={urllib.parse.quote_plus(query)}", embeds=embeds)

    def as_embed(self, pod) -> discord.Embed:
        embed = discord.Embed(title=pod.title)
        for sub in itertools.islice(pod.subpods, 10):
            if not embed.image and sub.img and sub.img.src:
                embed.set_image(url=sub.img.src)
            if sub.title:
                embed.add_field(name=sub.title, value=sub.plaintext)
            else:
                name = sub.img.title or sub.img.alt
                value = sub.plaintext
                if not (name is None or value is None or name == value):
                    embed.add_field(name=sub.img.title or sub.img.alt, value=sub.plaintext)
        return embed
