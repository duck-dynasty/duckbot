import random
from discord.ext import commands


class FormulaOne(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        red_a = "\U0001F170"
        red_b = "\U0001F171"
        self.phrases = [
            [  # car go fast
                self.chr("c"),
                self.chr("a"),
                self.chr("r"),
                self.chr("g"),
                self.chr("o"),
                self.chr("f"),
                red_a,
                self.chr("s"),
                self.chr("t"),
            ],
            [  # vet go sbin
                self.chr("v"),
                self.chr("e"),
                self.chr("t"),
                self.chr("g"),
                self.chr("o"),
                self.chr("s"),
                red_b,
                self.chr("i"),
                self.chr("n"),
            ],
            [self.chr("h"), self.chr("y"), self.chr("p"), self.chr("e")],
            [self.chr("p"), self.chr("o"), self.chr("g")],
        ]

    def chr(self, letter):
        regional_indicator_a = 0x0001F1E6
        return chr(ord(letter) - ord("a") + regional_indicator_a)

    @commands.Cog.listener("on_message")
    async def car_do_be_going_fast_though(self, message):
        if self.is_dank_channel(message.channel):
            for letter in random.choice(self.phrases):
                await message.add_reaction(letter)

    def is_dank_channel(self, channel):
        return channel.name == "dank"
