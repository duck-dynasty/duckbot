import pytest

from duckbot.cogs.text import MockText


@pytest.mark.asyncio
async def test_mock_text_mocks_message(bot, command_context):
    clazz = MockText(bot)
    await clazz.mock_text(command_context, "some' message% asd")
    command_context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    command_context.message.delete.assert_called()


@pytest.mark.asyncio
async def test_mock_text_no_message(bot, command_context):
    command_context.message.author.display_name = "bob"
    clazz = MockText(bot)
    await clazz.mock_text(command_context, "")
    command_context.send.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    command_context.message.delete.assert_called()
