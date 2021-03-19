from discord.ext import commands, tasks


class Emojis(commands.Cog, name="emojis"):
    """Provides access to server emojis.
    Currently assumes that DuckBot is only ever in a single server."""

    def __init__(self, bot, start_tasks=True):
        self.bot = bot
        self.guild = 0
        self.emojis = {}
        if start_tasks:
            self.refresh.start()

    def cog_unload(self):
        self.refresh.cancel()

    @commands.Cog.listener("on_ready")
    async def populate(self):
        self.__refresh(print_emojis=True)

    @tasks.loop(hours=24.0)
    async def refresh(self):
        self.__refresh()

    def __refresh(self, print_emojis=False):
        emojis = {}
        gid = 0
        for guild in self.bot.guilds:
            gid = guild.id
            emojis[gid] = {}
            for emoji in guild.emojis:
                if print_emojis:
                    print(f"registering emoji: {emoji}")
                emojis[gid][emoji.id] = emoji
        self.emojis = emojis
        self.guild = gid

    @refresh.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    def get_emoji_by_name(self, name):
        """Returns the emoji with the given name. Throws if it does not exist."""
        return next(emoji for emoji in self.emojis[self.guild].values() if emoji.name == name)

    def get_emoji(self, id):
        """Returns the emoji with the given id. Throws if it does not exist."""
        return self.emojis[self.guild][id]
