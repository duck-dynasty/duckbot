import pytest
from duckbot.cogs.robot import ThankingRobot


@pytest.mark.asyncio
async def test_correct_giving_thanks_bot_author(bot, message):
    bot.user = "THEBOT"
    message.content = "Thank you DuckBot."
    message.author = bot.user
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt"])
async def test_correct_giving_thanks_message_is_thanks(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author}")


@pytest.mark.asyncio
async def test_correct_giving_thanks_message_has_no_thanks(bot, message):
    bot.user = "but"
    message.author = "author"
    message.content = "you duck, suckbot"
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()
