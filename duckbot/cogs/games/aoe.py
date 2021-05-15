from discord.ext import commands

from duckbot.util.messages import try_delete

from .aoe_phrases import taunts


class AgeOfEmpires(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def expand_taunt(self, message):
        msg = message.content.strip()
        if msg in taunts:
            taunt = taunts[msg]
            await message.channel.send(f"{message.author.mention} > {msg}: _{taunt}_")
            await try_delete(message)
