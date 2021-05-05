import discord
from discord.ext import commands


class Kubernetes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.k8s = self.kubernetes = None

    @commands.Cog.listener("on_ready")
    async def store_emojis(self):
        self.k8s = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="k8s")
        self.kubernetes = discord.utils.get(self.bot.emojis, guild__name="Friends Chat", name="kubernetes")

    @commands.Cog.listener("on_message")
    async def correct_kubernetes(self, message):
        """Corrections for kubernetes"""

        if message.author == self.bot.user:
            return

        if self.kubernetes is not None and str(self.kubernetes) in message.content:
            await message.channel.send(f"I think {message.author.display_name} means {self.k8s}")
        else:
            kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
            for k in kubes:
                if k in message.content.lower():
                    await message.channel.send(f"I think {message.author.display_name} means K8s")
                    return

    @commands.Cog.listener("on_message")
    async def correct_k8s(self, message):
        """Corrections for K8s"""

        if message.author == self.bot.user:
            return

        if self.k8s is not None and str(self.k8s) in message.content:
            await message.channel.send(f"I think {message.author.display_name} means {self.kubernetes}")
        elif "k8" in message.content.lower():
            await message.channel.send(f"I think {message.author.display_name} means Kubernetes")
