import asyncio
from importlib.resources import path
from typing import Optional, Union

from discord import FFmpegPCMAudio, PCMVolumeTransformer, VoiceClient
from discord.ext import commands

from duckbot.slash import InteractionContext, slash_command
from duckbot.util.messages import try_delete


class WhoCanItBeNow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stream = asyncio.Event()
        self.voice_client: Optional[VoiceClient] = None
        self.audio_task = None
        self.streaming = False

    def cog_unload(self) -> Optional[asyncio.Task]:
        if self.streaming:
            return self.bot.loop.create_task(self.stop())

    @slash_command()
    @commands.command(name="start", description='Start playing "music" in whatever voice channel you are currently in.')
    async def start_command(self, context: Union[commands.Context, InteractionContext]):
        await self.start(context)

    @start_command.before_invoke
    async def connect_to_voice(self, context: Union[commands.Context, InteractionContext]):
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

    async def start(self, context: Union[commands.Context, InteractionContext]):
        """Starts the music loop if it is not already playing."""
        await context.send(":musical_note: :saxophone:", delete_after=30)
        if not self.streaming:
            self.streaming = True
            self.audio_task = self.bot.loop.create_task(self.stream_audio())

    async def stream_audio(self):
        """The music loop. Connect to channel and stream. We await on `self.stream` to block on the song being played."""
        play_count = 0
        while self.streaming and play_count < 75:
            self.stream.clear()
            # need to load the song every time, it seems to keep internal state
            with path("resources", "who-can-it-be-now.mp3") as source:
                song = PCMVolumeTransformer(FFmpegPCMAudio(source, options='-filter:a "volume=0.125"'))
            self.voice_client.play(song, after=self.trigger_next_song)
            play_count += 1
            await asyncio.sleep(0)  # give up timeslice for `trigger_next_song`
            await self.stream.wait()
        if self.streaming and not play_count < 75:
            await self.stop()

    def trigger_next_song(self, error=None):
        self.stream.set()
        if error:
            raise commands.CommandError(str(error))

    @slash_command()
    @commands.command(name="stop", description='Stop playing "music" entirely.')
    async def stop_command(self, context: Union[commands.Context, InteractionContext]):
        await self.stop(context)

    async def stop(self, context: Optional[Union[commands.Context, InteractionContext]] = None):
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
            if context:
                await context.send(":disappointed_relieved:", delete_after=30)
        elif context is not None:
            await context.send("Brother, no :musical_note: :saxophone: is active.", delete_after=30)

    @start_command.after_invoke
    @stop_command.after_invoke
    async def delete_command_message(self, context: Union[commands.Context, InteractionContext]):
        await try_delete(context.message)
