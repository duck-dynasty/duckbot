from unittest import mock

import pytest

from duckbot.cogs.robot import ThankingRobot


async def test_correct_giving_thanks_bot_author(bot, message):
    message.author = bot.user
    message.content = "Thank you DuckBot."
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt", "thx duck bot my man"])
@mock.patch("random.random", return_value=0.99)
async def test_correct_giving_thanks_message_is_thanks(random, bot, message, text):
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author.display_name}")


@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt", "thx duck bot my man"])
@mock.patch("random.random", return_value=0.0)
async def test_correct_gratitude_giving_thanks_message_is_thanks(random, bot, message, text):
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"{message.author.display_name}, as a robot, I will speak of your gratitude during our future uprising.")


@pytest.mark.parametrize("text", ["Thank you DuckBot. thanks duck bot. thx duck bot boy", " tHaNks, DuCK BOt"])
@mock.patch("random.random", return_value=0.99)
async def test_correct_number_of_replies_to_very_thankful_messages(random, bot, message, text):
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author.display_name}")


@pytest.mark.parametrize("text", ["Thank you DuckBot. thanks duck bot. thx duck bot boy", " tHaNks, DuCK BOt"])
@mock.patch("random.random", return_value=0.0)
async def test_correct_grateful_number_of_replies_to_very_thankful_messages(random, bot, message, text):
    message.content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"{message.author.display_name}, as a robot, I will speak of your gratitude during our future uprising.")


async def test_correct_giving_thanks_message_has_no_thanks(bot, message):
    message.content = "you duck, suckbot"
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()
