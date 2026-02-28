from unittest import mock

import discord
import pytest

from duckbot.cogs.corrections import Kubernetes


@pytest.fixture
def k8s_emoji(autospec, guild):
    guild.name = "Friends Chat"
    e = autospec.of(discord.Emoji)
    e.guild = guild
    e.id = 1
    e.name = "k8s"
    e.__str__ = lambda x: "<k8s:1>"
    return e


@pytest.fixture
def kubernetes_emoji(autospec, guild):
    guild.name = "Friends Chat"
    e = autospec.of(discord.Emoji)
    e.guild = guild
    e.id = 2
    e.name = "kubernetes"
    e.__str__ = lambda x: "<kubernetes:2>"
    return e


@pytest.fixture
def setup_emojis(bot, kubernetes_emoji, k8s_emoji):
    bot.emojis = [kubernetes_emoji, k8s_emoji]


async def test_store_emojis_emojis_exist(bot, kubernetes_emoji, k8s_emoji, setup_emojis):
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    assert clazz.k8s == k8s_emoji
    assert clazz.kubernetes == kubernetes_emoji


async def test_store_emojis_no_emojis_found(bot):
    bot.emojis = []
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    assert clazz.k8s is None
    assert clazz.kubernetes is None


async def test_correct_kubernetes_bot_author(bot, bot_message):
    bot_message.content = "kubernetes"
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(bot_message)
    bot_message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["koober nets", "kuber nets", "kubernets", "kubernetes", "kubernetes kubernets"])
async def test_correct_kubernetes_message_is_kubernetes(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means K8s")


@pytest.mark.parametrize("text", ["kuber", "k8s", "duckbot"])
async def test_correct_kubernetes_message_is_not_kubernetes(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_not_called()


async def test_correct_kubernetes_message_is_kubernetes_emoji_but_unknown(bot, message, kubernetes_emoji):
    message.content = str(kubernetes_emoji)
    clazz = Kubernetes(bot)
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means K8s")


async def test_correct_kubernetes_message_is_kubernetes_emoji(bot, message, kubernetes_emoji, k8s_emoji, setup_emojis):
    message.content = str(kubernetes_emoji)
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.correct_kubernetes(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means {k8s_emoji}")


async def test_correct_k8s_bot_author(bot, bot_message):
    bot_message.content = "k8s"
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(bot_message)
    bot_message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["k8", "k8s", "K8", "K8s", "K8S"])
async def test_correct_k8s_message_is_k8s(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means Kubernetes")


@pytest.mark.parametrize("text", ["kubernetes", "duckbot"])
async def test_correct_k8s_message_is_not_k8s(bot, message, text):
    message.content = text
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_not_called()


async def test_correct_k8s_message_is_k8s_emoji_but_unknown(bot, message, k8s_emoji):
    message.content = str(k8s_emoji)
    clazz = Kubernetes(bot)
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means Kubernetes")


async def test_correct_k8s_message_is_k8s_emoji(bot, message, kubernetes_emoji, k8s_emoji, setup_emojis):
    message.content = str(k8s_emoji)
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.correct_k8s(message)
    message.channel.send.assert_called_once_with(f"I think {message.author.display_name} means {kubernetes_emoji}")


@mock.patch("discord.RawReactionActionEvent")
async def test_react_to_k8s_reaction_not_either_emoji(payload, bot, setup_emojis):
    payload.emoji.name = "some-other-crap"
    payload.member.bot = False
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.react_to_k8s_reaction(payload)
    bot.fetch_channel.assert_not_called()


@pytest.mark.parametrize("name", ["kubernetes", "k8s"])
@mock.patch("discord.RawReactionActionEvent")
async def test_react_to_k8s_reaction_bot_sent_reaction(payload, name, bot, setup_emojis):
    payload.emoji.name = name
    payload.member.bot = True
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.react_to_k8s_reaction(payload)
    bot.fetch_channel.assert_not_called()


@pytest.mark.parametrize("name", ["kubernetes", "k8s"])
@mock.patch("discord.RawReactionActionEvent")
async def test_react_to_k8s_reaction_kubernetes_emoji(payload, name, bot, kubernetes_emoji, k8s_emoji, setup_emojis, channel, message):
    payload.emoji.name = name
    payload.member.bot = False
    payload.channel_id = 123
    payload.message_id = 456
    bot.fetch_channel.return_value = channel
    channel.fetch_message.return_value = message
    clazz = Kubernetes(bot)
    await clazz.store_emojis()
    await clazz.react_to_k8s_reaction(payload)
    bot.fetch_channel.assert_called_once_with(payload.channel_id)
    channel.fetch_message.assert_called_once_with(payload.message_id)
    message.add_reaction.assert_called_once_with(kubernetes_emoji if name == "k8s" else k8s_emoji)
