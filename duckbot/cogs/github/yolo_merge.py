import datetime
import os
from typing import Dict, List, Optional

import discord
import github
from discord.ext import commands
from discord.utils import utcnow
from github.PullRequest import PullRequest
from github.Repository import Repository

CHECK_PASSED = ":white_check_mark:"
CHECK_FAILED = ":x:"
CHECK_PENDING = ":coffee:"


async def is_repository_admin(context: commands.Context):
    """Disallow !yolo to be used outside of a server, and only allow the bot owner or
    repository owners to use it."""
    if context.guild is None:
        raise commands.NoPrivateMessage()
    if not await context.bot.is_owner(context.author) and context.author.id not in [368038054558171141, 776607982472921088, 375024417358479380]:
        raise commands.MissingPermissions(["repository admin"])
    return True


class YoloMerge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._github = None
        self.merge_confirmations: Dict[int, MergeConfirmation] = {}

    @property
    def github(self) -> github.Github:
        if self._github is None:
            self._github = github.Github(os.getenv("GITHUB_TOKEN"))
        return self._github

    @commands.command(name="yolo")
    @commands.check(is_repository_admin)
    async def yolo_command(self, context: commands.Context, pr_id: Optional[int] = None):
        async with context.typing():
            await self.yolo(context, pr_id)

    async def yolo(self, context: commands.Context, pr_id: Optional[int]):
        repo = self.github.get_repo("duck-dynasty/duckbot")
        if pr_id is None:
            await self.list(context, repo)
        else:
            await self.merge(context, repo, pr_id)

    async def list(self, context: commands.Context, repo: Repository):
        pulls = list(repo.get_pulls()[:6])
        if pulls:
            embed = self.as_embed(pulls)
            await context.send(embed=embed)
        else:
            await context.send("There's no open pull requests, brother. Never forget to wumbo.")

    def as_embed(self, prs: List[PullRequest]) -> discord.Embed:
        embed = discord.Embed()
        for pr in prs:
            embed.add_field(name=f"#{pr.number}", value="\n".join(self.get_pr_summary_lines(pr)))
        return embed

    def get_pr_summary_lines(self, pr: PullRequest) -> List[str]:
        lines = [
            f"[{pr.title}]({pr.html_url})",
            f"{pr.changed_files} changed file{'s' if pr.changed_files > 1 else ''}; +{pr.additions} -{pr.deletions}",
            f"mergeable {CHECK_PASSED if pr.mergeable else CHECK_FAILED}",
            f"up to date {CHECK_PASSED if pr.mergeable_state == 'blocked' else CHECK_FAILED}",
        ]
        return lines + self.get_checks_summary_lines(pr)

    def get_checks_summary_lines(self, pr: PullRequest) -> List[str]:
        lines = []
        commit = pr.get_commits().reversed[0]
        for suite in commit.get_check_suites():
            completed = suite.status == "completed"
            success = suite.conclusion == "success"
            if completed:
                result = CHECK_PASSED if success else CHECK_FAILED
            else:
                result = CHECK_PENDING
            lines.append(f"**{suite.app.name}** {result}")
        return lines

    async def merge(self, context: commands.Context, repo: Repository, pr_id: int):
        pr = repo.get_pull(pr_id)
        embed = self.as_embed([pr])
        mergeable = self.all_checks_passed(embed) and pr.state == "open"
        if self.has_valid_request(pr_id, context.author.id) and mergeable:
            self.merge_confirmations.pop(pr_id, None)
            pr.create_review(body="YOLO", event="APPROVE")
            pr.merge(commit_title=pr.title, commit_message="YOLO", merge_method="squash")
            await context.send("Welp. See you on the other side, brother.")
        elif mergeable:
            await context.send("Bruh, that'll merge this god-awful pull request... are you sure you trust it? Only Tom would push this...", embed=embed)
            self.merge_confirmations[pr_id] = MergeConfirmation(context.author.id, context.message.created_at)
        else:
            await context.send("Bruh. Come on. I can't merge this garbage.", embed=embed)

    def has_valid_request(self, pr_id: int, requester: int):
        stamp = utcnow() - datetime.timedelta(minutes=1)
        return pr_id in self.merge_confirmations and requester == self.merge_confirmations[pr_id].requester and stamp < self.merge_confirmations[pr_id].time

    def all_checks_passed(self, pull_embed: discord.Embed):
        blob = str(pull_embed.to_dict())
        return CHECK_PENDING not in blob and CHECK_FAILED not in blob


class MergeConfirmation:
    def __init__(self, requester: int, time: datetime.datetime):
        self._requester = requester
        self._time = time

    @property
    def requester(self) -> int:
        return self._requester

    @property
    def time(self) -> datetime.datetime:
        return self._time

    def __str__(self):
        return str({"requester": self.requester, "time": self.time})

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.requester == other.requester and self.time == other.time if isinstance(other, MergeConfirmation) else False
