from .interaction import Interaction
from .context import InteractionContext
from .option import Option, OptionType
from .core import slash_command, SlashCommandPatch


def setup(bot):
    bot.add_cog(SlashCommandPatch(bot))
