import pytest

from duckbot.cogs.robot import ThankingRobot


@pytest.mark.asyncio
async def test_correct_giving_thanks_bot_author(bot, message):
    message.author = bot.user
    message.content = "Thank you DuckBot."
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt"])
async def test_correct_giving_thanks_message_is_thanks(bot, message, text):
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author.display_name}")


@pytest.mark.asyncio
async def test_correct_giving_thanks_message_has_no_thanks(bot, message):
    message.content = "you duck, suckbot"
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()
