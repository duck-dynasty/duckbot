import calendar
from dataclasses import dataclass
from datetime import time, timedelta

from discord import ChannelType, Forbidden, Message
from discord.ext import commands, tasks
from discord.utils import get

import duckbot.util.datetime
from duckbot.util.users import get_user

LEADERBOARD_SIZE = 10
MIN_MESSAGES_FOR_AWARD = 25


@dataclass
class UserStats:
    messages: int = 0
    words: int = 0
    capital_starts: int = 0
    questions: int = 0
    shouts: int = 0
    links: int = 0


class FriendFacts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.friend_facts_loop.start()

    def cog_unload(self):
        self.friend_facts_loop.cancel()

    def get_general_channel(self):
        return get(self.bot.get_all_channels(), guild__name="Friends Chat", name="general", type=ChannelType.text)

    @tasks.loop(time=time(hour=9, minute=0, tzinfo=duckbot.util.datetime.timezone()))
    async def friend_facts_loop(self):
        await self.on_month_start()

    @friend_facts_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def on_month_start(self):
        if duckbot.util.datetime.now().day == 1:
            await self.send_report()

    @commands.command(name="friend-facts")
    async def friend_facts(self, context):
        await self.send_report()

    def prior_month_range(self):
        end = duckbot.util.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (end - timedelta(days=1)).replace(day=1)
        return start, end

    async def send_report(self):
        channel = self.get_general_channel()
        start, end = self.prior_month_range()
        stats, hours, days, channels = await self.gather_stats(channel.guild, start, end)
        await channel.send(await self.format_report(channel.guild, stats, hours, days, channels, start))

    async def gather_stats(self, guild, start, end):
        """Streams message history into counters; messages are never kept in memory."""
        stats = {}
        hours = [0] * 24
        days = [0] * 7
        channels = 0
        for channel in guild.text_channels:
            if not channel.permissions_for(guild.me).read_message_history:
                continue
            try:
                async for message in channel.history(limit=None, after=start, before=end, oldest_first=True):
                    if not message.author.bot:
                        self.tally(stats, hours, days, message)
                channels += 1
            except Forbidden:
                pass
        return stats, hours, days, channels

    def tally(self, stats, hours, days, message: Message):
        user = stats.setdefault(message.author.id, UserStats())
        content = message.content
        user.messages += 1
        user.words += len(content.split())
        user.capital_starts += content[:1].isupper()
        user.questions += content.rstrip().endswith("?")
        user.shouts += content.isupper() and any(c.isalpha() for c in content)
        user.links += "http" in content
        created = message.created_at.astimezone(duckbot.util.datetime.timezone())
        hours[created.hour] += 1
        days[created.weekday()] += 1

    async def format_report(self, guild, stats, hours, days, channels, start):
        header = f"**Friend Facts: {start:%B %Y}** :bar_chart:"
        if not stats:
            return f"{header}\nNobody said anything last month. :duck:"
        lines = [header, "```", f"{'User':<24} {'Messages':>8}", "-" * 34]
        top = sorted(stats.items(), key=lambda x: x[1].messages, reverse=True)
        for user_id, user in top[:LEADERBOARD_SIZE]:
            lines.append(f"{await self.display_name(guild, user_id):<24} {user.messages:>8}")
        lines.append("```")
        lines.append(f":pencil: {sum(u.messages for u in stats.values()):,} messages across {channels} channels")
        lines += await self.awards(guild, stats)
        lines.append(f":crescent_moon: Busiest hour: {self.hour_name(hours.index(max(hours)))} · Busiest day: {calendar.day_name[days.index(max(days))]}")
        return "\n".join(lines)

    async def awards(self, guild, stats):
        lines = []
        regulars = {k: v for k, v in stats.items() if v.messages >= MIN_MESSAGES_FOR_AWARD}
        if regulars:
            user_id, user = max(regulars.items(), key=lambda x: x[1].capital_starts / x[1].messages)
            lines.append(f":tophat: Grammar Police: {await self.display_name(guild, user_id)} — {100 * user.capital_starts // user.messages}% of messages start with a capital")
            user_id, user = max(regulars.items(), key=lambda x: x[1].words / x[1].messages)
            lines.append(f":books: Wordiest: {await self.display_name(guild, user_id)} — {user.words / user.messages:.1f} words per message")
            user_id, user = max(regulars.items(), key=lambda x: x[1].questions / x[1].messages)
            lines.append(f":question: Most Inquisitive: {await self.display_name(guild, user_id)} — {100 * user.questions // user.messages}% of messages are questions")
        user_id, user = max(stats.items(), key=lambda x: x[1].shouts)
        if user.shouts:
            lines.append(f":loudspeaker: Loudest: {await self.display_name(guild, user_id)} — {user.shouts} ALL-CAPS messages")
        user_id, user = max(stats.items(), key=lambda x: x[1].links)
        if user.links:
            lines.append(f":link: Chief Link Dumper: {await self.display_name(guild, user_id)} — {user.links} links shared")
        return lines

    async def display_name(self, guild, user_id):
        user = await get_user(self.bot, user_id, guild)
        return user.display_name if user else f"User-{user_id}"

    def hour_name(self, hour):
        return f"{hour % 12 or 12}{'am' if hour < 12 else 'pm'}"
