from .ascii_art import AsciiArt


def setup(bot):
    bot.add_cog(AsciiArt(bot))
