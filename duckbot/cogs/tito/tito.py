from discord.ext import commands
import asyncio
from .flags import flags


class Tito(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def react_to_tito_with_yugoslavia(self, message):
        """Adds reactions for all formally Yugoslavian country flags when :tito: is sent."""
        if ":tito:" in message.content:
            await asyncio.wait([message.add_reaction(f) for f in flags])

    @commands.Cog.listener("on_raw_reaction_add")
    async def react_to_tito_reaction(self, payload):
        """Adds reactions for all formally Yugoslavian country flags when :tito: is added as reaction."""
        if payload.emoji.name == "tito":
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await asyncio.wait([message.add_reaction(f) for f in flags])
