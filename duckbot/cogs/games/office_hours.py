from discord.ext import commands, tasks
import requests
from discord.utils import get
from discord import ChannelType


class OfficeHours(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.streaming = False
        self.check_if_streaming_loop.start()

    def cog_unload(self):
        self.check_if_streaming_loop.cancel()

    @tasks.loop(minutes=5.0)
    async def check_if_streaming_loop(self):
        await self.check_if_streaming()

    async def check_if_streaming(self):
        page = requests.get("https://www.twitch.tv/conlabx").content.decode("utf-8")
        streaming = "isLiveBroadcast" in page
        if streaming != self.streaming:
            self.streaming = streaming
            if streaming:
                channel = get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)
                await channel.send("Office Hours have started!\nhttps://www.twitch.tv/conlabx")

    @check_if_streaming_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
