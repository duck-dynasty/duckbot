import pytest
from unittest import mock
from discord import Embed, Colour
from duckbot.cogs.fortune import EightBall


@pytest.mark.asyncio
async def test_eightball_no_text(bot, context):
    clazz = EightBall(bot)
    await clazz.eightball(context, None)
    context.send.assert_called_once_with("You need to ask a question to get an answer. :unamused:")


@pytest.mark.asyncio
async def test_eightball_not_given_question(bot, context):
    clazz = EightBall(bot)
    await clazz.eightball(context, "not a question")
    context.send.assert_called_once_with("I can't tell if that's a question, brother.")


@pytest.mark.asyncio
@pytest.mark.parametrize("question", ["?", "???"])
async def test_eightball_only_question_marks(bot, context, question):
    clazz = EightBall(bot)
    await clazz.eightball(context, question)
    context.send.assert_called_once_with("Who do you think you are? I AM!\nhttps://youtu.be/gKQOXYB2cd8?t=10")


@pytest.mark.asyncio
@mock.patch("random.choice", return_value="8ball")
@mock.patch("random.random", return_value=0.5)
async def test_eightball_gives_response(choice, random, bot, context):
    clazz = EightBall(bot)
    await clazz.eightball(context, "will this test pass?")
    embed = Embed(colour=Colour.purple()).add_field(name=f"{context.author.nick}, my :crystal_ball: says:", value="_8ball_")
    context.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
@mock.patch("random.choice", side_effect=["joke", "fortune"])
@mock.patch("random.random", return_value=0.29)
async def test_eightball_gives_joke_response(choice, random, bot, context):
    clazz = EightBall(bot)
    await clazz.eightball(context, "will this test pass?")
    context.send.assert_any_call("joke")
    embed = Embed(colour=Colour.purple()).add_field(name=f"{context.author.nick}, my :crystal_ball: says:", value="_fortune_")
    context.send.assert_any_call(embed=embed)
