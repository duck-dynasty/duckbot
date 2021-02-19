from discord.ext import commands
import asyncio

class Tito(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.flags = [
            "\U0001F1E7\U0001F1E6", # :flag_ba:
            "\U0001F1ED\U0001F1F7", # :flag_hr:
            "\U0001F1FD\U0001F1F0", # :flag_xk:
            "\U0001F1F2\U0001F1EA", # :flag_me:
            "\U0001F1F2\U0001F1F0", # :flag_mk:
            "\U0001F1F7\U0001F1F8", # :flag_rs:
            "\U0001F1F8\U0001F1EE", # :flag_si:
        ]

    @commands.Cog.listener('on_message')
    async def react_to_tito_with_yugoslavia(self, message):
        """Adds reactions for all formally Yugoslavian country flags when :tito: is sent."""

        if message.author == self.bot.user:
            return

        if ":tito:" in message.content:
            await asyncio.wait([message.add_reaction(f) for f in self.flags])
