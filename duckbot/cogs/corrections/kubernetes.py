import discord
from discord.ext import commands


class Kubernetes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def store_emojis(self):
        self.k8s = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="k8s")
        self.kubernetes = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="kubernetes")

    @commands.Cog.listener("on_message")
    async def correct_kubernetes(self, message):
        """Corrections for kubernetes"""

        if message.author == self.bot.user:
            return

        if str(self.kubernetes) in message.content:
            await message.channel.send(f"I think {message.author.nick} means {self.k8s}")
        else:
            kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
            for k in kubes:
                if k in message.content.lower():
                    correction = f"I think {message.author.nick} means K8s"
                    await message.channel.send(correction)

    @commands.Cog.listener("on_message")
    async def correct_k8s(self, message):
        """Corrections for K8s"""

        if message.author == self.bot.user:
            return

        if str(self.k8s) in message.content:
            await message.channel.send(f"I think {message.author.nick} means {self.kubernetes}")
        elif "k8" in message.content.lower():
            correction = f"I think {message.author.nick} means Kubernetes"
            await message.channel.send(correction)
