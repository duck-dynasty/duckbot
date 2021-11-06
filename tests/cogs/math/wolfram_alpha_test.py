import discord
import pytest
import wolframalpha

from duckbot.cogs.math import WolframAlpha
from duckbot.util.embeds import MAX_EMBED_LENGTH, MAX_TITLE_LENGTH


@pytest.fixture
def wra_client(autospec) -> wolframalpha.Client:
    return autospec.of(wolframalpha.Client)


@pytest.fixture
def wolfram(bot, wra_client) -> WolframAlpha:
    clazz = WolframAlpha(bot)
    clazz._wolfram = wra_client
    return clazz


def test_wolfram_creates_instance(bot, monkeypatch):
    monkeypatch.setenv("WOLFRAM_ALPHA_TOKEN", "token")
    clazz = WolframAlpha(bot)
    assert clazz.wolfram == clazz._wolfram


def test_wolfram_returns_cached_instance(wolfram, wra_client):
    wolfram._wolfram = wra_client
    assert wolfram.wolfram == wra_client


@pytest.mark.asyncio
async def test_calc_single_pod(wolfram, context, wra_client):
    wra_client.query.return_value = result([pod(subpods=[subpod(img=image())])])
    await wolfram.calc(context, "query")
    embed = discord.Embed(title="title").set_image(url="src").add_field(name="subtitle", value="plaintext")
    context.send.assert_called_once_with("https://www.wolframalpha.com/input/?i=query", embeds=[embed])


@pytest.mark.asyncio
async def test_calc_single_pod_large_embed(wolfram, context, wra_client):
    wra_client.query.return_value = result([pod(title="p" * MAX_EMBED_LENGTH, subpods=[subpod(title="s" * MAX_EMBED_LENGTH, plaintext="t" * MAX_EMBED_LENGTH, img=image())])])
    await wolfram.calc(context, "query")
    embed = discord.Embed(title="p" * MAX_TITLE_LENGTH).set_image(url="src").add_field(name="s" * 64, value="t" * 512)
    context.send.assert_called_once_with("https://www.wolframalpha.com/input/?i=query", embeds=[embed])


@pytest.mark.asyncio
async def test_calc_multiple_pods_and_subpods(wolfram, context, wra_client):
    wra_client.query.return_value = result(
        [
            pod(title="pod1", subpods=[subpod(title="1"), subpod(title="2", img=image(src="2.img"))]),
            pod(title="pod2", subpods=[subpod(title="3")]),
            pod(title="pod3", subpods=[subpod(title=None, img=image(title="img", src="pod3.img"))]),
        ]
    )
    await wolfram.calc(context, "query things")
    embed1 = discord.Embed(title="pod1").set_image(url="2.img").add_field(name="1", value="plaintext").add_field(name="2", value="plaintext")
    embed2 = discord.Embed(title="pod2").add_field(name="3", value="plaintext")
    embed3 = discord.Embed(title="pod3").set_image(url="pod3.img").add_field(name="img", value="plaintext")
    context.send.assert_called_once_with("https://www.wolframalpha.com/input/?i=query+things", embeds=[embed1, embed2, embed3])


def result(pods=None):
    return MockResult(pods)


def pod(title="title", subpods=None):
    return MockPod(title, subpods)


def subpod(title="subtitle", plaintext="plaintext", img=None):
    return MockSubPod(title, plaintext, img)


def image(title="img", src="src", alt="alt"):
    return MockImage(title, src, alt)


class MockResult:
    def __init__(self, pods):
        self.pods = pods if pods else []


class MockPod:
    def __init__(self, title, subpods):
        self.title = title
        self.subpods = subpods


class MockSubPod:
    def __init__(self, title, plaintext, img):
        self.title = title
        self.plaintext = plaintext
        self.img = img


class MockImage:
    def __init__(self, title="img", src="src", alt="alt"):
        self.title = title
        self.src = src
        self.alt = alt
