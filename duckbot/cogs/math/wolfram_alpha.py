import os

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
