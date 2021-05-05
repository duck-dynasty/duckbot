import pytest
from unittest import mock
from duckbot.cogs.corrections import Kubernetes


@pytest.fixture
@mock.patch("discord.Emoji", autospec=True)
def k8s_emoji(e, guild):
    guild.name = "Friends Chat"
    e.guild = guild
    e.id = 1
    e.name = "k8s"
    e.__str__ = lambda x: "<k8s:1>"
    return e


@pytest.fixture
@mock.patch("discord.Emoji", autospec=True)
def kubernetes_emoji(e, guild):
    guild.name = "Friends Chat"
    e.guild = guild
    e.id = 2
    e.name = "kubernetes"
    e.__str__ = lambda x: "<kubernetes:2>"
    return e


@pytest.fixture
def setup_emojis(bot, kubernetes_emoji, k8s_emoji):
    bot.emojis = [kubernetes_emoji, k8s_emoji]


@pytest.mark.asyncio
async def test_store_emojis_emojis_exist(bot, kubernetes_emoji, k8s_emoji, setup_emojis):
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    assert clazz.k8s == k8s_emoji
    assert clazz.kubernetes == kubernetes_emoji


@pytest.mark.asyncio
async def test_store_emojis_no_emojis_found(bot):
    bot.emojis = []
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    assert clazz.k8s is None
    assert clazz.kubernetes is None


@pytest.mark.asyncio
async def test_correct_kubernetes_bot_author(bot, message):
    message.author = bot.user
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["koober nets", "kuber nets", "kubernets", "kubernetes", "kubernetes kubernets"])
async def test_correct_kubernetes_message_is_kubernetes(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means K8s")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["kuber", "k8s", "duckbot"])
async def test_correct_kubernetes_message_is_not_kubernetes(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_correct_kubernetes_message_is_kubernetes_emoji_but_unknown(bot, message, kubernetes_emoji):
    message.content = str(kubernetes_emoji)
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means K8s")


@pytest.mark.asyncio
async def test_correct_kubernetes_message_is_kubernetes_emoji(bot, message, kubernetes_emoji, k8s_emoji, setup_emojis):
    message.content = str(kubernetes_emoji)
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means {k8s_emoji}")


@pytest.mark.asyncio
async def test_correct_k8s_bot_author(bot, message):
    message.author = bot.user
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["k8", "k8s", "K8", "K8s", "K8S"])
async def test_correct_k8s_message_is_k8s(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means Kubernetes")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["kubernetes", "duckbot"])
async def test_correct_k8s_message_is_not_k8s(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_correct_k8s_message_is_k8s_emoji_but_unknown(bot, message, k8s_emoji):
    message.content = str(k8s_emoji)
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means Kubernetes")


@pytest.mark.asyncio
async def test_correct_k8s_message_is_k8s_emoji(bot, message, kubernetes_emoji, k8s_emoji, setup_emojis):
    message.content = str(k8s_emoji)
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means {kubernetes_emoji}")
