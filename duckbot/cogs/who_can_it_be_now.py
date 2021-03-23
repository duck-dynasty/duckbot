import os
import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio


class WhoCanItBeNow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream = asyncio.Event()
        self.client = None
        self.player = None
        self.streaming = False

    @commands.command("start")
    async def start(self, context):
        if not self.streaming:
            self.streaming = True
            self.player = self.bot.loop.create_task(self.stream_audio())
        else:
            await context.send("Already streaming, you fool!")

    async def stream_audio(self):
        while self.streaming:
            self.stream.clear()
            if self.client is None or not self.client.is_connected():
                channel = self.bot.get_cog("channels").get_channel_by_name("Hangout 1")
                self.client = await channel.connect()
            song = FFmpegPCMAudio(os.path.join(os.path.dirname(__file__), "..", "..", "resources", "who-can-it-be-now.mp3"), options='-filter:a "volume=0.125"')
            self.client.play(song, after=self.trigger_next_song)
            await self.stream.wait()

    def trigger_next_song(self, error=None):
        self.stream.set()

    @commands.command("stop")
    async def stop(self, context):
        if self.streaming:
            self.streaming = False
            if self.client is not None:
                await self.client.disconnect()
            self.client = None
        else:
            await context.send("Nothing to stop, you fool!")
