import asyncio
from discord.ext import commands
from discord import FFmpegPCMAudio
from importlib.resources import path


class WhoCanItBeNow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream = asyncio.Event()
        self.client = None
        self.player = None
        self.streaming = False

    @commands.Cog.listener("on_error")
    @commands.Cog.listener("on_disconnect")
    async def stop_if_running(self, error=None):
        if self.streaming:
            await self.__stop(None)

    @commands.command("start")
    async def start(self, context):
        await self.__start(context)

    async def __start(self, context):
        """Starts the music loop if it is not already playing."""
        if not self.streaming:
            self.streaming = True
            self.player = asyncio.create_task(self.stream_audio())
        else:
            await context.send("Already streaming, you fool!")

    async def stream_audio(self):
        """The music loop. Connect to channel and stream. We await on `self.stream` to block on the song being played."""
        while self.streaming:
            self.stream.clear()
            if self.client is None or not self.client.is_connected():
                self.client = await self.bot.get_cog("channels").get_channel_by_name("Hangout 1").connect()
            # need to load the song every time, it seems to keep internal state
            with path("resources", "who-can-it-be-now.mp3") as source:
                song = FFmpegPCMAudio(source, options='-filter:a "volume=0.125"')
            self.client.play(song, after=self.trigger_next_song)
            await asyncio.sleep(0)  # give up timeslice for `trigger_next_song`
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
                if self.client.is_playing():
                    self.client.stop()
                await self.client.disconnect()
            self.client = None
            self.player = None
        else:
            await context.send("Nothing to stop, you fool!")
