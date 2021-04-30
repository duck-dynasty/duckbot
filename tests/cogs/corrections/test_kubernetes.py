import pytest
from duckbot.cogs.corrections import Kubernetes


@pytest.mark.asyncio
async def test_correct_kubernetes_bot_author(bot, message):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["koober nets", "kuber nets", "kubernets", "kubernetes"])
async def test_correct_kubernetes_message_is_kubernetes(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author} means K8s")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["kuber", "k8s", "duckbot"])
async def test_correct_kubernetes_message_is_not_kubernetes(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_correct_k8s_bot_author(bot, message):
    bot.user = "THEBOT"
    message.author = bot.user
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["k8", "k8s", "K8", "K8s", "K8S"])
async def test_correct_k8s_message_is_k8s(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author} means Kubernetes")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["kubernetes", "duckbot"])
async def test_correct_k8s_message_is_not_k8s(bot, message, text):
    bot.user = "but"
    message.author = "author"
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_not_called()
