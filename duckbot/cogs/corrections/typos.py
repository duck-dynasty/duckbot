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

    def get_wiki_corrections(self):
        request = urllib.request.Request("https://en.wikipedia.org/wiki/Wikipedia:Lists_of_common_misspellings/For_machines")
        html_content = urllib.request.urlopen(request).read()
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.findAll("pre")[-1].get_text()
        return {line[0]: line[1].split(", ") for line in (x.split("->") for x in text.splitlines())}

    def __get_custom_corrections(self):
        return {
            "fcuk": ["fuck"],
            "fcuking": ["fucking"],
            "gud": ["good"],
            "hye": ["hey"],
            "prety": ["pretty"],
            "ta": ["at"],
            "thats": ["that's"],
            "wut": ["what"],
            "wat": ["what"],
        }

    @tasks.loop(hours=24.0)
    async def refresh_corrections(self):
        self.corrections = {**self.get_wiki_corrections(), **self.__get_custom_corrections()}

    @refresh_corrections.before_loop
    async def before_refresh_corrections(self):
        self.corrections = {**self.get_wiki_corrections(), **self.__get_custom_corrections()}
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_message")
    async def correct_typos(self, message):
        await self.__correct_typos(message)

    async def __correct_typos(self, message):
        """Try to correct common typos for user's previous message."""
        if message.content.strip().lower() == "fuck":
            prev = await self.__get_previous_message(message)
            if prev is not None:
                c = self.correct(prev.content)
                if c != prev.content:
                    msg = f"> {c}\nThink I fixed it, {message.author.mention}!"
                    await message.channel.send(msg)
                else:
                    await message.channel.send(f"There's no need for harsh words, {message.author.mention}.")

    def correct(self, str):
        words = str.split()
        correction = []
        modified = False
        for w in words:
            word = w.lower()
            if word in self.corrections:
                correction.append(self.corrections[word][0])
                modified = True
            else:
                correction.append(w)
        if modified:
            return " ".join(correction)
        else:
            return str

    async def __get_previous_message(self, message):
        # limit of 20 may be restricting, since it includes everyone's messages
        hist = await message.channel.history(limit=20, before=message).flatten()
        by_same_author = list(x for x in hist if x.author.id == message.author.id)
        if not by_same_author:
            return None
        else:
            return by_same_author[0]
