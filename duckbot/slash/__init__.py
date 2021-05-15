from .interaction import Interaction
from .context import InteractionContext
from .option import Option, OptionType
from .core import slash_command


def setup(bot):
    from .core import SlashCommandPatch

    bot._patch_slash_commands = SlashCommandPatch(bot)
    bot.add_cog(bot._patch_slash_commands)
