import discord
import pytest

from duckbot.cogs.google import LetMeGoogleThat
from tests.discord_test_ext import bind_commands


@pytest.fixture
def clazz() -> LetMeGoogleThat:
    return bind_commands(LetMeGoogleThat())


async def test_let_me_google_that_generates_link(clazz, context):
    await clazz.let_me_google_that(context, query="search thing")
    context.send.assert_called_once_with(embed=discord.Embed().add_field(name="search thing", value="[https://google.com/search?q=search+thing](https://letmegooglethat.com/?q=search+thing)"))
    context.message.delete.assert_called()
