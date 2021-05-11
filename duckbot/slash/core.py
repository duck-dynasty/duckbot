from discord.ext.commands import Command, Context


class SlashCommand:
    async def invoke(self, context: Context):
        pass

    async def dispatch_error(self, context: Context, error):
        pass


def slash(name, description=None):
    pass
