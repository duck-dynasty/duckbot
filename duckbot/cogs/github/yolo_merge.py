import os
from typing import List, Optional

import discord
import github
from discord.ext import commands
from github.PullRequest import PullRequest


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

    def github(self) -> github.Github:
        if self._github is None:
            self._github = github.Github(os.getenv("GITHUB_TOKEN"))
        return self._github

    @commands.command(name="yolo")
    @commands.check(is_repository_admin)
    async def yolo_command(self, context: commands.Context, pr_id: Optional[int] = None):
        await self.yolo(context, pr_id)

    async def yolo(self, context: commands.Context, pr_id: Optional[int]):
        await self.list(context)

    async def list(self, context: commands.Context):
        repo = self.github().get_repo("duck-dynasty/duckbot")
        embed = self.as_embed(list(repo.get_pulls()[:10]))
        await context.send(embed=embed)

    def as_embed(self, prs: List[PullRequest]) -> discord.Embed:
        embed = discord.Embed()
        for pr in prs:
            commit = [c for c in pr.get_commits()][-1]
            check_results = []
            for suite in commit.get_check_suites():
                completed = suite.status == "completed"
                success = suite.conclusion == "success"
                if completed:
                    result = ":white_check_mark:" if success else ":x:"
                else:
                    result = ":coffee:"
                check_results.append(f"**{suite.app.name}** {result}")
            check_results = "\n".join(check_results)
            embed.add_field(
                name=f"#{pr.number}",
                value=f"""
                    [{pr.title}]({pr.html_url})
                    {pr.changed_files} changed file{"s" if pr.changed_files > 1 else ""}; +{pr.additions} -{pr.deletions}
                    Pull is {"" if pr.mergeable else "NOT "} mergeable. It is currently {pr.mergeable_state}.
                    {check_results}
                """,
            )
        return embed
