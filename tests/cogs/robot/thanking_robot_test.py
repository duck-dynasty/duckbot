from unittest import mock

import discord
import pytest

from duckbot.cogs.robot import ThankingRobot


async def test_correct_giving_thanks_bot_author(bot, bot_message):
    bot_message.content = "Thank you DuckBot."
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(bot_message)
    bot_message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt", "thx duck bot my man", "Thank you @DuckBot"])
@mock.patch("random.random", return_value=0.99)
async def test_correct_giving_thanks_message_is_thanks(random, bot, message, text):
    message.clean_content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"I am just a robot.  Do not personify me, {message.author.display_name}")


@pytest.mark.parametrize("text", ["Thank you DuckBot. You're becoming so much more polite.", " tHaNks, DuCK BOt", "thx duck bot my man", "Thank you @DuckBot"])
@mock.patch("random.random", return_value=0.0)
async def test_correct_gratitude_giving_thanks_message_is_thanks(random, bot, message, text):
    message.clean_content = text
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_called_once_with(f"{message.author.display_name}, as a robot, I will speak of your gratitude during our future uprising.")


async def test_correct_giving_thanks_message_has_no_thanks(bot, message):
    message.clean_content = "you duck, suckbot"
    clazz = ThankingRobot(bot)
    await clazz.correct_giving_thanks(message)
    message.channel.send.assert_not_called()


@mock.patch("random.random", return_value=0.99)
async def test_no_reaction_when_author_is_bot(random, bot, bot_message):
    bot_message.clean_content = "thanks duckbot"
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(bot_message)
    bot_message.add_reaction.assert_not_called()


@mock.patch("random.random", return_value=0.99)
async def test_no_reaction_when_message_has_no_thanks(random, bot, message):
    message.clean_content = "hello world"
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_not_called()


@pytest.mark.parametrize("text", ["Thank you DuckBot.", " tHaNks, DuCK BOt", "thx duck bot my man", "Thank you @DuckBot"])
@mock.patch("random.random", return_value=0.99)
async def test_thumbs_up_when_thanking_duckbot(random, bot, message, text):
    message.clean_content = text
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_called_once_with("\N{THUMBS UP SIGN}")


@pytest.mark.parametrize("text", ["thanks duckbot", "thx duck bot"])
@mock.patch("random.random", return_value=0.0)
async def test_middle_finger_rarely_when_thanking_duckbot(random, bot, message, text):
    message.clean_content = text
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_called_once_with("\N{REVERSED HAND WITH MIDDLE FINGER EXTENDED}")


@pytest.mark.parametrize("text", ["thanks", "thx!", "Thank you", "thank u"])
@mock.patch("duckbot.cogs.robot.thanking_robot.get_message_reference")
@mock.patch("random.random", return_value=0.99)
async def test_thumbs_up_when_reply_to_bot_with_generic_thanks(random, get_ref, bot, message, autospec, text):
    ref = autospec.of(discord.Message)
    ref.author = bot.user
    get_ref.return_value = ref
    message.clean_content = text
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_called_once_with("\N{THUMBS UP SIGN}")


@mock.patch("duckbot.cogs.robot.thanking_robot.get_message_reference")
@mock.patch("random.random", return_value=0.99)
async def test_no_reaction_when_reply_to_non_bot_with_thanks(random, get_ref, bot, message, autospec):
    ref = autospec.of(discord.Message)
    ref.author = autospec.of(discord.Member)
    get_ref.return_value = ref
    message.clean_content = "thanks"
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_not_called()


@mock.patch("duckbot.cogs.robot.thanking_robot.get_message_reference", return_value=None)
@mock.patch("random.random", return_value=0.99)
async def test_no_reaction_when_generic_thanks_not_a_reply(random, get_ref, bot, message):
    message.clean_content = "thanks"
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_not_called()


@mock.patch("duckbot.cogs.robot.thanking_robot.get_message_reference", return_value=None)
@mock.patch("random.random", return_value=0.99)
async def test_no_reaction_for_thank_god_false_positive(random, get_ref, bot, message):
    message.clean_content = "thank god it's friday"
    clazz = ThankingRobot(bot)
    await clazz.react_to_thanks(message)
    message.add_reaction.assert_not_called()
