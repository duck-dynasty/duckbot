from .ascii_art import AsciiArt
from .dictionary import Dictionary
from .mock_text import MockText


def setup(bot):
    bot.add_cog(AsciiArt(bot))
    bot.add_cog(MockText(bot))
    bot.add_cog(Dictionary(bot))
