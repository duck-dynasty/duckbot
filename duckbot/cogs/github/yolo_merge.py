import discord
from discord.ext import commands
from typing import Optional, List
import datetime
import os
from github import Github
from github.PullRequest import PullRequest


async def is_repository_admin(context: commands.Context):
    # if context.guild is None:
    #     raise commands.NoPrivateMessage()
    if not await context.bot.is_owner(context.author) and context.author.id not in []:
        raise commands.MissingPermissions(["repository admin"])
    return True


class YoloMerge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.approvals = {}
        self._github = None

    def github(self) -> Github:
        if self._github is None:
            self._github = Github(os.getenv("GITHUB_TOKEN"))
        return self._github

    @commands.command(name="yolo")
    @commands.check(is_repository_admin)
    async def yolo_command(self, context: commands.Context, pr_id: Optional[int] = None):
        await self.yolo(context, pr_id)

    async def yolo(self, context: commands.Context, pr_id: Optional[int]):
        if pr_id is None:
            await self.list(context)
        else:
            await self.merge(context, pr_id)

    async def list(self, context: commands.Context):
        repo = self.github().get_repo("duck-dynasty/duckbot")
        embed = self.as_embed(list(repo.get_pulls()[:10]))
        await context.send(embed=embed)

    def as_embed(self, prs: List[PullRequest]) -> discord.Embed:
        embed = discord.Embed()
        # TODO add checks, reviews, etc
        for pr in prs:
            embed.add_field(inline=False, name=f"#{pr.number}", value=f"""
            [{pr.title}]({pr.html_url})
            {pr.changed_files} changed file{"s" if pr.changed_files > 1 else ""}; +{pr.additions} -{pr.deletions}
            Pull is {"" if pr.mergeable else "NOT "} mergeable. It is currently {pr.mergeable_state}.
            """)
        return embed

    async def merge(self, context: commands.Context, pr_id: int):
        if pr_id in self.approvals:
            pass
        else:
            self.approvals[pr_id] = datetime.datetime.now()
