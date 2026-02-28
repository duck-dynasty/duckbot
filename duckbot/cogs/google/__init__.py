from .let_me_google_that import LetMeGoogleThat


async def setup(bot):
    await bot.add_cog(LetMeGoogleThat())
