from .context import InteractionContext
from .interaction import Interaction
from .option import Option, OptionType
from .slash_command import slash_command
from .slash_command_patch import SlashCommandPatch


def setup(bot):
    bot.add_cog(SlashCommandPatch(bot))
