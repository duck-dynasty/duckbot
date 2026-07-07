from .ascii_art import AsciiArt
from .mock_text import MockText
from .wordnik import Wordnik


async def setup(bot):
    await bot.add_cog(AsciiArt())
    await bot.add_cog(MockText())
    await bot.add_cog(Wordnik(bot))
