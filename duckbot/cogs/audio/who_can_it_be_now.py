import asyncio
from importlib.resources import path

from discord import FFmpegPCMAudio, PCMVolumeTransformer, VoiceClient
from discord.ext import commands

from duckbot.util.messages import try_delete


class WhoCanItBeNow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream = asyncio.Event()
        self.voice_client: VoiceClient = None
        self.audio_task = None
        self.streaming = False

    def cog_unload(self):
        if self.streaming:
            return self.bot.loop.create_task(self.__stop())

    @commands.command("start")
    async def start(self, context):
        await self.__start(context)

    @start.before_invoke
    async def connect_to_voice(self, context):
        if context.voice_client is None:
            if not hasattr(context.author, "voice"):
                await context.send("Music can only be played in a discord server, not a private channel.", delete_after=30)
            elif context.author.voice:
                self.voice_client = await context.author.voice.channel.connect()
            else:
                await context.send("Connect to a voice channel so I know where to `!start`.", delete_after=30)
                raise commands.CommandError("`start` invoked when author not in voice channel")
        else:
            context.voice_client.stop()

    async def __start(self, context):
        """Starts the music loop if it is not already playing."""
        if not self.streaming:
            self.streaming = True
            self.audio_task = self.bot.loop.create_task(self.stream_audio())

    async def stream_audio(self):
        """The music loop. Connect to channel and stream. We await on `self.stream` to block on the song being played."""
        while self.streaming:
            self.stream.clear()
            # need to load the song every time, it seems to keep internal state
            with path("resources", "who-can-it-be-now.mp3") as source:
                song = PCMVolumeTransformer(FFmpegPCMAudio(source, options='-filter:a "volume=0.125"'))
            self.voice_client.play(song, after=self.trigger_next_song)
            await asyncio.sleep(0)  # give up timeslice for `trigger_next_song`
            await self.stream.wait()

    def trigger_next_song(self, error=None):
        self.stream.set()
        if error:
            raise commands.CommandError(str(error))

    @commands.command("stop")
    async def stop(self, context):
        await self.__stop(context)

    async def __stop(self, context=None):
        """Stops the music loop if it is playing."""
        if self.streaming:
            await self.voice_client.disconnect()
            try:
                self.audio_task.cancel()
                await self.audio_task
            except asyncio.CancelledError:
                self.audio_task = None
            self.voice_client = None
            self.streaming = False
        elif context is not None:
            await context.send("Brother, no :musical_note: :saxophone: is active.", delete_after=30)

    @start.after_invoke
    @stop.after_invoke
    async def delete_command_message(self, context):
        await try_delete(context.message)
