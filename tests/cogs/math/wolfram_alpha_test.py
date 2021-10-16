import pytest
import wolframalpha

from duckbot.cogs.math import WolframAlpha


@pytest.fixture
def wra_client(autospec) -> wolframalpha.Client:
    return autospec.of("wolframalpha.Client")


@pytest.fixture
def wolfram(bot) -> WolframAlpha:
    clazz = WolframAlpha(bot)
    return clazz


def test_github_creates_instance(bot, monkeypatch):
    monkeypatch.setenv("WOLFRAM_ALPHA_TOKEN", "token")
    clazz = WolframAlpha(bot)
    assert clazz.wolfram == clazz._wolfram


def test_github_returns_cached_instance(wolfram, wra_client):
    wolfram._wolfram = wra_client
    assert wolfram.wolfram == wra_client
