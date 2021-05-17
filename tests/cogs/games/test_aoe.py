import pytest

from duckbot.cogs.games import AgeOfEmpires


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["105", "  105  "])
async def test_expand_taunt_message_is_taunt(bot, message, text):
    message.content = text
    clazz = AgeOfEmpires(bot)
    await clazz.expand_taunt(message)
    message.channel.send.assert_called_once_with(f"{message.author.mention} > 105: _You can resign again._")
    message.delete.assert_called()


@pytest.mark.asyncio
async def test_expand_taunt_message_is_not_taunt(bot, message):
    message.content = "0"
    clazz = AgeOfEmpires(bot)
    await clazz.expand_taunt(message)
    message.channel.send.assert_not_called()
    message.delete.assert_not_called()
