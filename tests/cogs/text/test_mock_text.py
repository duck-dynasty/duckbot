import pytest

from duckbot.cogs.text import MockText


@pytest.mark.asyncio
async def test_mock_text_mocks_message(bot, context):
    clazz = MockText(bot)
    await clazz.mock_text(context, "some' message% asd")
    context.send.assert_called_once_with("SoMe' MeSsAgE% aSd")
    context.message.delete.assert_called()


@pytest.mark.asyncio
async def test_mock_text_message_too_long(bot, context):
    clazz = MockText(bot)
    await clazz.mock_text(context, "a " * 999)
    context.send.assert_called_once_with("ThAt'S tOo MuCh LeTtErS aNd StUfF dUdE.")
    context.message.delete.assert_called()
