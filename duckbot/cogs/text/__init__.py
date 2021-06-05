from .ascii_art import AsciiArt
from .mock_text import MockText


def setup(bot):
    bot.add_cog(AsciiArt(bot))
    bot.add_cog(MockText(bot))
