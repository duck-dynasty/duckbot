import pytest
import mock
from duckbot.cogs import Kubernetes


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_kubernetes_bot_author(message, bot):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Kubernetes(bot)
    assert await clazz.correct_kubernetes(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [("koober nets"), ("kuber nets"), ("kubernets"), ("kubernetes")])
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_kubernetes_message_is_kubernetes(message, bot, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    assert await clazz.correct_kubernetes(message) is None
    message.channel.send.assert_called_once_with(f"I think {message.author} means K8s")


@pytest.mark.asyncio
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_k8s_bot_author(message, bot):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Kubernetes(bot)
    assert await clazz.correct_k8s(message) is None
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [("k8"), ("k8s"), ("K8"), ("K8s"), ("K8S")])
@mock.patch("discord.Message")
@mock.patch("discord.ext.commands.Bot")
async def test_correct_k8s_message_is_k8s(message, bot, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    assert await clazz.correct_k8s(message) is None
    message.channel.send.assert_called_once_with(f"I think {message.author} means Kubernetes")
