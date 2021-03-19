from discord.ext import commands


class Kubernetes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_kubernetes(self, message):
        """Corrections for kubernetes"""

        if message.author == self.bot.user:
            return

        kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
        for k in kubes:
            if k in message.content.lower():
                author = str(message.author).split("#")[0]
                correction = f"I think {author} means K8s"
                await message.channel.send(correction)

    @commands.Cog.listener("on_message")
    async def correct_k8s(self, message):
        """Corrections for K8s"""

        if message.author == self.bot.user:
            return

        if "k8" in message.content.lower():
            author = str(message.author).split("#")[0]
            correction = f"I think {author} means Kubernetes"
            await message.channel.send(correction)
