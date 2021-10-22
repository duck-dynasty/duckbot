from typing import Tuple
from unittest import mock

import discord
import github
import github.CheckSuite
import github.Commit
import github.PullRequest
import github.Repository
import pytest

from duckbot.cogs.github import YoloMerge


@pytest.fixture
def repo(autospec) -> github.Repository.Repository:
    return autospec.of(github.Repository.Repository)


@pytest.fixture
def gh(autospec) -> github.Github:
    return autospec.of(github.Github)


@pytest.fixture
def yolo(bot, gh) -> YoloMerge:
    clazz = YoloMerge(bot)
    clazz._github = gh
    return clazz


def test_github_creates_instance(bot, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    clazz = YoloMerge(bot)
    assert clazz.github == clazz._github


def test_github_returns_cached_instance(yolo, gh):
    yolo._github = gh
    assert yolo.github == gh


@pytest.mark.asyncio
async def test_list_no_pulls(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pulls.return_value = []
    await yolo.list(context)
    context.send.assert_called_once_with("There's no open pull requests, brother. Never forget to wumbo.")


@pytest.mark.asyncio
async def test_list_send_pull_status(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    pull, embed_value = make_pull_request(1)
    repo.get_pulls.return_value = [pull]
    await yolo.list(context)
    context.send.assert_called_once_with(embed=discord.Embed().add_field(name="#1", value=embed_value))


@pytest.mark.asyncio
async def test_list_max_six_pulls(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    all_pulls = [make_pull_request(i, i % 2 == 0) for i in range(15)]
    kept_pulls = all_pulls[:6]
    repo.get_pulls.return_value = [p[0] for p in all_pulls]
    await yolo.list(context)
    embed = discord.Embed()
    for pull, embed_value in kept_pulls:
        embed = embed.add_field(name=f"#{pull.number}", value=embed_value)
    context.send.assert_called_once_with(embed=embed)


def make_pull_request(number: int, mergeable=True) -> Tuple[github.PullRequest.PullRequest, str]:
    pull = pr()
    pull.number = number
    pull.changed_files = 10
    pull.additions = 50
    pull.deletions = 25
    pull.mergeable = mergeable
    pull.mergeable_status = "blocked" if mergeable else "behind"
    commits = MockPaginatedList([commit(), commit(), commit()])
    pull.get_commits.return_value = commits
    last_commit = commits[-1]
    success_check = check_suite()
    success_check.status = "completed"
    success_check.conclusion = "success"
    failure_check = check_suite()
    failure_check.status = "completed"
    failure_check.conclusion = "failed"
    incomplete_check = check_suite()
    incomplete_check.status = "queued"
    incomplete_check.conclusion = "pending"
    last_commit.get_check_suites.return_value = [success_check, failure_check, incomplete_check]

    lines = [
        f"[{pull.title}]({pull.html_url})",
        "10 changed files; +50 -25",
        "mergeable :white_check_mark:" if pull.mergeable else "mergeable :x:",
        "up to date :white_check_mark:" if pull.mergeable_state == "blocked" else "up to date :x:",
        f"**{success_check.app.name}** :white_check_mark:",
        f"**{failure_check.app.name}** :x:",
        f"**{incomplete_check.app.name}** :coffee:",
    ]
    return pull, "\n".join(lines)


@mock.patch("github.PullRequest.PullRequest")
def pr(p) -> github.PullRequest.PullRequest:
    return p


@mock.patch("github.Commit.Commit")
def commit(c) -> github.Commit.Commit:
    return c


@mock.patch("github.CheckSuite.CheckSuite")
def check_suite(c) -> github.CheckSuite.CheckSuite:
    return c


class MockPaginatedList(list):
    @property
    def reversed(self):
        copy = [x for x in self]
        copy.reverse()
        return copy
