import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

class Typos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.corrections = {}
        self.refresh_corrections.start()

    def cog_unload(self):
        self.refresh_corrections.cancel()

    def get_corrections(self):
        request = urllib.request.Request("https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines")
        html_content = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.findAll("pre")[-1].get_text()
        return { l[0]: l[1].split(", ") for l in (x.split("->") for x in text.splitlines()) }

    @tasks.loop(hours = 24.0)
    async def refresh_corrections(self):
        self.corrections = self.get_corrections()

    @refresh_corrections.before_loop
    async def before_refresh_corrections(self):
        await self.bot.wait_until_ready()
