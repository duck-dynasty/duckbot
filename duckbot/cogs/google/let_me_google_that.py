import urllib.parse

import discord
from discord.ext import commands

from duckbot.util.messages import try_delete


class LetMeGoogleThat(commands.Cog):
    @commands.command(name="lmgt")
    async def let_me_google_that_command(self, context: commands.Context, *, query: str):
        await self.let_me_google_that(context, query)

    async def let_me_google_that(self, context: commands.Context, query: str):
        text = f"https://google.com/search?q={urllib.parse.quote_plus(query)}"
        link = f"https://letmegooglethat.com/?q={urllib.parse.quote_plus(query)}"
        embed = discord.Embed().add_field(name=query, value=f"[{text}]({link})")
        await context.send(embed=embed)
        await try_delete(context.message)
