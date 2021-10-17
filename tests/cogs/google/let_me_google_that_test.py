import discord
import pytest

from duckbot.cogs.google import LetMeGoogleThat


@pytest.mark.asyncio
async def test_let_me_google_that_generates_link(bot, context):
    clazz = LetMeGoogleThat(bot)
    await clazz.let_me_google_that(context, "search thing")
    context.send.assert_called_once_with(embed=discord.Embed().add_field(name="search thing", value="[Google It!](https://letmegooglethat.com/?q=search+thing)"))
    context.message.delete.assert_called()
