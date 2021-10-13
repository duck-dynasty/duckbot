from unittest import mock

import pytest

from duckbot.cogs.github import YoloMerge


@pytest.fixture
@mock.patch("github.Github")
def github(g):
    return g


@pytest.fixture
def clazz(bot, github):
    claz = YoloMerge(bot)
    claz._owm_client = github
    return claz


def test_github_creates_instance(bot, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    claz = YoloMerge(bot)
    assert claz.github() == claz._github


def test_github_returns_cached_instance(clazz, github):
    clazz._github = github
    assert clazz.github() == github
