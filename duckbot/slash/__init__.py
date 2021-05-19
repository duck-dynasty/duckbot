from .context import InteractionContext
from .core import SlashCommandPatch
from .interaction import Interaction
from .option import Option, OptionType
from .slash_command import slash_command


def setup(bot):
    bot.add_cog(SlashCommandPatch(bot))
