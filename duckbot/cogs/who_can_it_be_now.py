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
        await self.__start(context)

    async def __start(self, context):
        """Starts the music loop if it is not already playing."""
        if not self.streaming:
            self.streaming = True
            self.player = self.bot.loop.create_task(self.stream_audio())
        else:
            await context.send("Already streaming, you fool!")

    async def stream_audio(self):
        """The music loop. Connect to channel and stream. We await on `self.stream` to block on the song being played."""
        while self.streaming:
            self.stream.clear()
            if self.client is None or not self.client.is_connected():
                channel = self.bot.get_cog("channels").get_channel_by_name("Hangout 1")
                self.client = await channel.connect()
            # need to load the song every time, it seems to keep internal state
            song = FFmpegPCMAudio(self.bot.get_cog("resources").get("who-can-it-be-now.mp3"), options='-filter:a "volume=0.125"')
            self.client.play(song, after=self.trigger_next_song)
            await self.stream.wait()

    def trigger_next_song(self, error=None):
        self.stream.set()

    @commands.command("stop")
    async def stop(self, context):
        await self.__stop(context)

    async def __stop(self, context):
        """Stops the music loop if it is playing."""
        if self.streaming:
            self.streaming = False
            if self.client is not None:
                await self.client.disconnect()
            self.client = None
        else:
            await context.send("Nothing to stop, you fool!")
