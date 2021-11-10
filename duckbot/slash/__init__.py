from .context import InteractionContext
from .option import Option, OptionType
from .slash_command_decorator import slash_command
from .slash_command_handler import SlashCommandHandler


def setup(bot):
    bot.add_cog(SlashCommandHandler(bot))
