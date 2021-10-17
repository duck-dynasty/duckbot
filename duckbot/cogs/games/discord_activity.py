import random

import discord
from discord.ext import commands, tasks


class DiscordActivity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.change_activity_loop.start()

    def cog_unload(self):
        self.change_activity_loop.cancel()

    @tasks.loop(minutes=281)
    async def change_activity_loop(self):
        # docs mention there's a "high chance" of disconnecting when changing the presence shortly after connecting
        # however, the issue was never replicated in testing with @loop, the docs specifically mention on_ready event
        # at any rate, if this fails a bunch, we can consider doing something as simple as sleeping a bit here maybe
        # https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-set-the-playing-status
        await self.change_activity()

    async def change_activity(self):
        await self.bot.change_presence(activity=self.random_activity())

    def random_activity(self):
        return random.choice(
            [
                discord.Game("Duck Game"),
                discord.Game("the Banjo"),
                discord.Game("Gloomhaven"),
                discord.Game("with Fire"),
                discord.Game("with the Boys"),
            ]
        )

    @change_activity_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
