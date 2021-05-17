from .context import InteractionContext
from .core import SlashCommandPatch, slash_command
from .interaction import Interaction
from .option import Option, OptionType


def setup(bot):
    bot.add_cog(SlashCommandPatch(bot))
