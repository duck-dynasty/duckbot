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
        await self.correct(message, ["koober nets", "kuber nets", "kubernets", "kubernetes"], "K8s", self.kubernetes, self.k8s)

    @commands.Cog.listener("on_message")
    async def correct_k8s(self, message):
        """Corrections for K8s"""
        await self.correct(message, ["k8"], "Kubernetes", self.k8s, self.kubernetes)

    async def correct(self, message, wrongs, right, wrong_emoji, right_emoji):
        if message.author == self.bot.author:
            return
        if wrong_emoji and right_emoji and str(wrong_emoji) in message.content:
            await message.channel.send(f"I think {message.author.display_name} means {right_emoji}")
        else:
            content = message.content.lower()
            for s in wrongs:
                if s in content:
                    await message.channel.send(f"I think {message.author.display_name} means {right}")
                    return
