import discord

from duckbot.cogs.google import LetMeGoogleThat


async def test_let_me_google_that_generates_link(bot, context):
    clazz = LetMeGoogleThat()
    await clazz.let_me_google_that(context, "search thing")
    context.send.assert_called_once_with(embed=discord.Embed().add_field(name="search thing", value="[https://google.com/search?q=search+thing](https://letmegooglethat.com/?q=search+thing)"))
    context.message.delete.assert_called()
