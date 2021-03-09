from discord.ext import commands, tasks


class Channels(commands.Cog, name="channels"):
    """Provides access to server channels.
    Currently assumes that DuckBot is only ever in a single server."""

    def __init__(self, bot, start_tasks=True):
        self.bot = bot
        self.guild = 0
        self.channels = {}
        if start_tasks:
            self.refresh.start()

    def cog_unload(self):
        self.refresh.cancel()

    @commands.Cog.listener('on_ready')
    async def populate(self):
        self.__refresh(print_channels=True)

    @tasks.loop(hours=24.0)
    async def refresh(self):
        self.__refresh()

    def __refresh(self, print_channels=False):
        channels = {}
        gid = 0
        for guild in self.bot.guilds:
            gid = guild.id
            channels[gid] = {}
            for channel in guild.channels:
                if print_channels:
                    print(f"registering channel: {channel.id} (#{channel.name})")
                channels[gid][channel.id] = channel
        self.channels = channels
        self.guild = gid

    @refresh.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    def get_channel_by_name(self, name):
        """Returns the channel with the given name. Throws if it does not exist."""
        return next(channel for channel in self.channels[self.guild].values() if channel.name == name)

    def get_channel(self, id):
        """Returns the channel with the given id. Throws if it does not exist."""
        return self.channels[self.guild][id]

    def get_general_channel(self):
        """Returns the general channel. Throws if it does not exist."""
        return self.get_channel_by_name("general")
