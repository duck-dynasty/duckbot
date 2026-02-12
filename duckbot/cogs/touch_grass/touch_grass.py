import datetime
import random

from discord import Message
from discord.ext import commands
from discord.utils import utcnow

from .touch_grass_phrases import phrases, work_phrases


class TouchGrass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = {}

    @commands.Cog.listener("on_message")
    async def on_message_activity(self, message: Message):
        """Monitor message activity and notify users who are too active."""
        if message.author == self.bot.user:
            return
        await self.track_activity(message)

    async def track_activity(self, message: Message):
        """Track user message activity and send notification if threshold is reached."""
        user_id = message.author.id
        now = utcnow()

        # Initialize tracking for new users
        if user_id not in self.activity:
            self.activity[user_id] = {"messages": [], "last_notification": None}

        # Add current message timestamp
        self.activity[user_id]["messages"].append(now)

        # Clean up old messages (outside 60-minute window)
        self.clean_old_messages(user_id, now)

        # Check if we should notify — lower threshold during work hours
        message_count = len(self.activity[user_id]["messages"])
        work_hours = self.is_work_hours(now)
        threshold = 40 if work_hours else 120
        if message_count >= threshold and self.should_notify(user_id, now):
            await self.send_notification(message, message_count, work_hours)
            self.activity[user_id]["last_notification"] = now

    def is_work_hours(self, now) -> bool:
        """Check if current time is Mon-Fri 9am-5pm UTC."""
        return now.weekday() < 5 and 9 <= now.hour < 17

    def clean_old_messages(self, user_id: int, now):
        """Remove timestamps older than 60 minutes from the tracking window."""
        cutoff = now - datetime.timedelta(hours=1)
        self.activity[user_id]["messages"] = [ts for ts in self.activity[user_id]["messages"] if ts > cutoff]

    def should_notify(self, user_id: int, now) -> bool:
        """Check if cooldown period has elapsed since last notification."""
        last_notif = self.activity[user_id].get("last_notification")
        if last_notif is None:
            return True
        return (now - last_notif).total_seconds() >= 3600  # 1 hour

    async def send_notification(self, message: Message, count: int, work_hours: bool):
        """Send a notification — work-themed during work hours, touch grass otherwise."""
        phrase_list = work_phrases if work_hours else phrases
        phrase = random.choice(phrase_list).format(name=message.author.display_name, count=count)
        await message.channel.send(phrase)

    @commands.hybrid_command(name="grass-stats", description="Show activity leaderboard for all tracked users.")
    async def grass_stats_command(self, context: commands.Context):
        """Show activity leaderboard for all tracked users."""
        await self.show_activity_stats(context)

    async def show_activity_stats(self, context):
        """Show activity leaderboard with current message counts."""
        now = utcnow()

        # Clean up old messages and collect stats
        stats = []
        for user_id, data in self.activity.items():
            # Clean old messages for this user
            cutoff = now - datetime.timedelta(hours=1)
            data["messages"] = [ts for ts in data["messages"] if ts > cutoff]

            count = len(data["messages"])
            if count > 0:  # Only show users with recent activity
                stats.append((user_id, count))

        if not stats:
            await context.send("No recent activity tracked in the last hour.")
            return

        # Sort by count descending (most active first)
        stats.sort(key=lambda x: x[1], reverse=True)

        # Format as table
        lines = ["**Activity Leaderboard (Last 60 Minutes)**", "```"]
        lines.append(f"{'User':<24} {'Messages':>8}")
        lines.append("-" * 34)

        for user_id, count in stats:
            # Try to get display name from guild
            member = context.guild.get_member(user_id) if context.guild else None
            if member:
                name = member.display_name[:22]  # Truncate long names
            else:
                # Fallback: try to get from bot's cache
                user = self.bot.get_user(user_id)
                name = user.display_name[:22] if user else f"User-{user_id}"

            lines.append(f"{name:<24} {count:>8}")

        lines.append("```")
        await context.send("\n".join(lines))
