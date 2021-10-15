import os
from typing import List, Optional

import discord
import github
from discord.ext import commands
from github.PullRequest import PullRequest

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
        await self.list(context)

    async def list(self, context: commands.Context):
        repo = self.github.get_repo("duck-dynasty/duckbot")
        pulls = list(repo.get_pulls()[:6])
        if pulls:
            embed = self.as_embed(pulls)
            await context.send(embed=embed)
        else:
            await context.send("There's no open pull requests, brother. Never forget to wumbo.")

    def as_embed(self, prs: List[PullRequest]) -> discord.Embed:
        embed = discord.Embed()
        for pr in prs:
            lines = [
                f"[{pr.title}]({pr.html_url})",
                f"{pr.changed_files} changed file{'s' if pr.changed_files > 1 else ''}; +{pr.additions} -{pr.deletions}",
                f"mergeable {CHECK_PASSED if pr.mergeable else CHECK_FAILED}",
                f"up to date {CHECK_PASSED if pr.mergeable_state == 'blocked' else CHECK_FAILED}",
            ]
            commit = pr.get_commits().reversed[0]
            for suite in commit.get_check_suites():
                completed = suite.status == "completed"
                success = suite.conclusion == "success"
                if completed:
                    result = CHECK_PASSED if success else CHECK_FAILED
                else:
                    result = CHECK_PENDING
                lines.append(f"**{suite.app.name}** {result}")
            embed.add_field(name=f"#{pr.number}", value="\n".join(lines))
        return embed
