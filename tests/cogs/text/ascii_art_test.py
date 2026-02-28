from unittest import mock

from duckbot.cogs.text import AsciiArt


@mock.patch("pyfiglet.figlet_format", return_value="ascii text")
async def test_ascii_formats_message(figlet, context):
    clazz = AsciiArt()
    await clazz.ascii(context, "some text")
    context.send.assert_called_once_with("```ascii text```")
    figlet.assert_called_once_with("some text")


@mock.patch("pyfiglet.figlet_format", side_effect=["x" * 2000, "happy birthday"])
async def test_ascii_message_too_long(figlet, context):
    clazz = AsciiArt()
    await clazz.ascii(context, "it text")
    context.send.assert_called_once_with("Discord won't let me send art with that much GUSTO, so here's a happy birthday.\n```happy birthday```")
    figlet.assert_any_call("it text")
    figlet.assert_any_call("Happy Birthday!")
