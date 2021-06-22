import pytest

from duckbot.cogs.text import MockText


@pytest.mark.asyncio
async def test_mock_text_mocks_message(bot, context):
    clazz = MockText(bot)
    await clazz.mock_text(context, "some' message% asd")
    context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    context.message.delete.assert_called()


@pytest.mark.asyncio
async def test_mock_text_no_message(bot, context):
    context.message.author.display_name = "bob"
    clazz = MockText(bot)
    await clazz.mock_text(context, "")
    context.send.assert_called_once_with("BoB, bAsEd On ThIs, I sHoUlD mOcK yOu... I nEeD tExT dUdE.")
    context.message.delete.assert_called()
