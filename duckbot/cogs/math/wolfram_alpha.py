import itertools
import os
import urllib.parse

import discord
import wolframalpha
from discord.ext import commands

from duckbot.util.embeds import MAX_EMBED_LENGTH, MAX_TITLE_LENGTH


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
    async def calc_command(self, context: commands.Context, *, query: str = "charizard curve"):
        async with context.typing():
            await self.calc(context, query)

    async def calc(self, context: commands.Context, query: str):
        result = self.wolfram.query(query)
        embeds = [self.as_embed(pod) for pod in itertools.islice(result.pods, 5)]
        await context.send(f"https://www.wolframalpha.com/input/?i={urllib.parse.quote_plus(query)}", embeds=embeds)

    # see embed limits duckbot.util.embeds; some values are shorter here for legibility
    def as_embed(self, pod) -> discord.Embed:
        embed = discord.Embed(title=pod.title[:MAX_TITLE_LENGTH])
        for sub in itertools.islice(pod.subpods, 10):
            if not embed.image and sub.img and sub.img.src:
                embed.set_image(url=sub.img.src)
            if sub.title:
                embed.add_field(name=sub.title[:64], value=sub.plaintext[:512])
            else:
                name = sub.img.title or sub.img.alt
                value = sub.plaintext
                if not (name is None or value is None or name == value):
                    embed.add_field(name=sub.img.title[:64] or sub.img.alt[:64], value=sub.plaintext[:512])
            if len(embed) > MAX_EMBED_LENGTH:
                embed.remove_field(len(embed.fields) - 1)  # we tried adding it, but we just can't do it, cap'n
        return embed
