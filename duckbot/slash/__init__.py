from .interaction import Interaction
from .context import InteractionContext
from .option import Option, OptionType
from .core import slash_command


def setup(bot):
    from .core import SlashCommandPatch

    bot.add_cog(SlashCommandPatch(bot))
