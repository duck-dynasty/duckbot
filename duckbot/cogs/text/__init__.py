from .ascii_art import AsciiArt
from .dictionary import Dictionary
from .mock_text import MockText


async def setup(bot):
    await bot.add_cog(AsciiArt(bot))
    await bot.add_cog(MockText(bot))
    await bot.add_cog(Dictionary(bot))
