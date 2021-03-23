import pytest
import mock
from duckbot.cogs import ThankingRobot


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_giving_thanks_bot_author(message, bot):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = ThankingRobot(bot)
    msg = await clazz.correct_giving_thanks(message)
    assert msg is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_bitcoin_message_is_bitcoin(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = "Thank you DuckBot. You're becoming so much more polite."
    clazz = ThankingRobot(bot)
    msg = await clazz.correct_giving_thanks(message)
    assert msg is None
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author}")


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_bitcoin_message_contains_bitcoin(message, bot):
    bot.user = "but"
    message.author = "author"
    message.content = " tHaNks, DuCK BOt"
    clazz = ThankingRobot(bot)
    msg = await clazz.correct_giving_thanks(message)
    assert msg is None
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author}")
