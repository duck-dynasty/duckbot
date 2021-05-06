from discord.ext import commands
import urllib
from discord import Embed, Colour


class Haiku(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.syllables = {}

    @commands.Cog.listener("on_ready")
    async def build_syllable_dictionary(self):
        data = urllib.request.urlopen(urllib.request.Request("https://raw.githubusercontent.com/Alexir/CMUdict/master/cmudict-0.7b"))
        syllables = {}
        for bline in data:
            line = bline.decode("latin1").strip()
            if line and line[0] != ";":  # ; are comments
                tokens = line.split()
                count = len([t for t in tokens[1:] if t[-1].isdigit()])
                syllables[tokens[0].lower()] = count
        self.syllables = syllables

    @commands.Cog.listener("on_message")
    async def detect_haiku(self, message):
        if message.author == self.bot.user:
            return
        words = self.get_words(message)
        i = 0
        lines = []
        for target_syllables in [5, 7, 5]:
            line = self.get_haiku_line(words[i:], target_syllables)
            if line is not None:
                i += len(line)
                lines.append(" ".join(line))
            else:
                return  # it's not a haiku
        haiku = "\n".join(lines)
        embed = Embed(colour=Colour.dark_red()).add_field(name=":cherry_blossom: **Haiku Detected** :cherry_blossom:", value=f"_{haiku}_")
        await message.channel.send(embed=embed)

    def get_words(self, message):
        return message.clean_content.replace(",", "").replace(".", "").replace("!", "").replace("?", "").split()

    def get_haiku_line(self, words, target):
        i = 0
        syls = 0
        line = []
        while target > 0 and i < len(words):
            word = words[i].lower()
            if word in self.syllables:
                line.append(words[i])
                target -= self.syllables[word]
                i += 1
            else:
                return None
        if target == 0:
            return line
        else:
            return None
