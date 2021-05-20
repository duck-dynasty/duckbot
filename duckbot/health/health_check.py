import asyncio

import discord
from discord.ext import commands


class HealthCheck(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def start_health_check_tasks(self):
        await asyncio.start_server(self.healthcheck, host="127.0.0.1", port=8008, loop=self.bot.loop)

    def healthcheck(self, reader, writer):
        if self.bot.user is None or not self.bot.is_ready() or self.bot.is_closed() or self.bot.latency > 1.0:
            writer.write(b"unhealthy")
        else:
            writer.write(b"healthy")
        writer.close()
