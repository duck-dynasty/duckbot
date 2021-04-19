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

    def cog_unload(self):
        if self.streaming:
            task = self.bot.loop.create_task(self.__stop(None))
            self.bot.loop.run_until_complete(task)

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
        self.client = await self.bot.get_cog("channels").get_channel_by_name("Hangout 1").connect()
        while self.streaming:
            self.stream.clear()
            # need to load the song every time, it seems to keep internal state
            with path("resources", "who-can-it-be-now.mp3") as source:
                song = FFmpegPCMAudio(source, options='-filter:a "volume=0.125"')
            self.client.play(song, after=self.trigger_next_song)
            await asyncio.sleep(0)  # give up timeslice for `trigger_next_song`
            await self.stream.wait()

    def trigger_next_song(self, error=None):
        if error:
            raise commands.CommandError(str(error))
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
            if self.player is not None:
                try:
                    self.player.cancel()
                    await self.player
                except asyncio.CancelledError:
                    self.player = None
        else:
            await context.send("Nothing to stop, you fool!")
