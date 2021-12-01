import datetime
import random
from typing import Tuple
from unittest import mock

import discord
import github
import github.CheckSuite
import github.Commit
import github.PullRequest
import github.Repository
import pytest
from github.GithubException import UnknownObjectException

from duckbot.cogs.github import YoloMerge
from duckbot.cogs.github.yolo_merge import MergeConfirmation


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
async def test_yolo_list_no_pulls(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pulls.return_value = []
    await yolo.yolo(context, None)
    context.send.assert_called_once_with("There's no open pull requests, brother. Never forget to wumbo.")


@pytest.mark.asyncio
async def test_yolo_list_send_pull_status(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    pull, embed_value = make_pull_request(1)
    repo.get_pulls.return_value = [pull]
    await yolo.yolo(context, None)
    context.send.assert_called_once_with(embed=discord.Embed().add_field(name="#1", value=embed_value))


@pytest.mark.asyncio
async def test_yolo_list_max_six_pulls(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    all_pulls = [make_pull_request(i, i % 2 == 0) for i in range(15)]
    kept_pulls = all_pulls[:6]
    repo.get_pulls.return_value = [p[0] for p in all_pulls]
    await yolo.yolo(context, None)
    embed = discord.Embed()
    for pull, embed_value in kept_pulls:
        embed = embed.add_field(name=f"#{pull.number}", value=embed_value)
    context.send.assert_called_once_with(embed=embed)


@pytest.mark.asyncio
async def test_yolo_merge_invalid_pull(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pull.side_effect = UnknownObjectException(status=404, data=None, headers=None)
    with pytest.raises(UnknownObjectException):
        await yolo.yolo(context, 404)
    repo.get_pull.assert_called_once_with(404)


@pytest.mark.asyncio
async def test_yolo_merge_checks_failed(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pull.return_value, embed_value = make_pull_request(101, mergeable=True, checks_passed=False)
    await yolo.yolo(context, 101)
    repo.get_pull.assert_called_once_with(101)
    context.send.assert_called_once_with("Bruh. Come on. I can't merge this garbage.", embed=discord.Embed().add_field(name="#101", value=embed_value))


@pytest.mark.asyncio
async def test_yolo_merge_not_mergeable(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pull.return_value, embed_value = make_pull_request(101, mergeable=False, checks_passed=True)
    await yolo.yolo(context, 101)
    repo.get_pull.assert_called_once_with(101)
    context.send.assert_called_once_with("Bruh. Come on. I can't merge this garbage.", embed=discord.Embed().add_field(name="#101", value=embed_value))


@pytest.mark.asyncio
async def test_yolo_merge_mergeable_first_attempt(yolo, context, gh, repo, skip_if_private_channel):
    gh.get_repo.return_value = repo
    repo.get_pull.return_value, embed_value = make_pull_request(101, mergeable=True, checks_passed=True)
    await yolo.yolo(context, 101)
    embed = discord.Embed().add_field(name="#101", value=embed_value)
    repo.get_pull.assert_called_once_with(101)
    context.send.assert_called_once_with("Bruh, that'll merge this god-awful pull request... are you sure you trust it? Only Tom would push this...", embed=embed)
    assert yolo.merge_confirmations == {101: MergeConfirmation(context.author.id, context.message.created_at)}


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.github.yolo_merge.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_yolo_merge_mergeable_second_attempt_late(utcnow, yolo, context, gh, repo, skip_if_private_channel):
    context.message.created_at = utcnow()
    yolo.merge_confirmations = {101: MergeConfirmation(context.author.id, utcnow() - datetime.timedelta(minutes=1, seconds=1))}
    gh.get_repo.return_value = repo
    repo.get_pull.return_value, embed_value = make_pull_request(101, mergeable=True, checks_passed=True)
    await yolo.yolo(context, 101)
    embed = discord.Embed().add_field(name="#101", value=embed_value)
    repo.get_pull.assert_called_once_with(101)
    context.send.assert_called_once_with("Bruh, that'll merge this god-awful pull request... are you sure you trust it? Only Tom would push this...", embed=embed)
    assert yolo.merge_confirmations == {101: MergeConfirmation(context.author.id, context.message.created_at)}


@pytest.mark.asyncio
@mock.patch("duckbot.cogs.github.yolo_merge.utcnow", return_value=datetime.datetime(2000, 1, 1, hour=12, minute=00, tzinfo=datetime.timezone.utc))
async def test_yolo_merge_mergeable_second_attempt_merges_yolo_bruh(utcnow, yolo, context, gh, repo, skip_if_private_channel):
    context.message.created_at = utcnow()
    yolo.merge_confirmations = {101: MergeConfirmation(context.author.id, utcnow() - datetime.timedelta(seconds=59))}
    gh.get_repo.return_value = repo
    pull = make_pull_request(101, mergeable=True, checks_passed=True)[0]
    repo.get_pull.return_value = pull
    await yolo.yolo(context, 101)
    repo.get_pull.assert_called_once_with(101)
    assert 101 not in yolo.merge_confirmations
    pull.create_review.assert_called_once_with(body="YOLO", event="APPROVE")
    pull.merge.assert_called_once_with(commit_title=pull.title, commit_message="YOLO", merge_method="squash")
    context.send.assert_called_once_with("Welp. See you on the other side, brother.")


def make_pull_request(number: int, mergeable=True, checks_passed=False) -> Tuple[github.PullRequest.PullRequest, str]:
    pull = pr()
    pull.number = number
    pull.changed_files = 10
    pull.additions = 50
    pull.deletions = 25
    pull.mergeable = mergeable
    pull.mergeable_state = "blocked" if mergeable else "behind"
    pull.state = "open" if mergeable else "closed"
    commits = MockPaginatedList([commit(), commit(), commit()])
    pull.get_commits.return_value = commits
    last_commit = commits[-1]
    success_check = check_suite()
    success_check.status = "completed"
    success_check.conclusion = random.choice(["success", "skipped", "neutral"])
    failure_check = check_suite()
    failure_check.status = "completed"
    failure_check.conclusion = "failed"
    incomplete_check = check_suite()
    incomplete_check.status = "queued"
    incomplete_check.conclusion = None
    if checks_passed:
        last_commit.get_check_suites.return_value = [success_check, success_check, success_check]
        lines = [
            f"[{pull.title}]({pull.html_url})",
            "10 changed files; +50 -25",
            "mergeable :white_check_mark:" if pull.mergeable else "mergeable :x:",
            "up to date :white_check_mark:" if pull.mergeable_state == "blocked" else "up to date :x:",
            f"**{success_check.app.name}** :white_check_mark:",
            f"**{success_check.app.name}** :white_check_mark:",
            f"**{success_check.app.name}** :white_check_mark:",
        ]
    else:
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
