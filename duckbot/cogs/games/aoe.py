import discord
from discord.ext import commands

from duckbot.util.messages import get_message_reference, try_delete

from .aoe_phrases import taunts


class AgeOfEmpires(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def expand_taunt(self, message: discord.Message):
        content = message.content.strip()
        if content in taunts:
            taunt = taunts[content]
            msg = f"{message.author.mention} > {content}: _{taunt}_"
            reply = await get_message_reference(message)
            if reply:
                await reply.reply(msg)
            else:
                await message.channel.send(msg)
            await try_delete(message)
