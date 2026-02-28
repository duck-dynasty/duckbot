from .ascii_art import AsciiArt
from .dictionary import Dictionary
from .mock_text import MockText


async def setup(bot):
    await bot.add_cog(AsciiArt())
    await bot.add_cog(MockText())
    await bot.add_cog(Dictionary(bot))
