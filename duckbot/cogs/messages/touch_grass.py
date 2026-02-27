import datetime
import random

from discord import Message
from discord.ext import commands
from discord.utils import utcnow

from .touch_grass_phrases import phrases, work_phrases

# Notification thresholds
WORK_HOURS_THRESHOLD = 40
OFF_HOURS_THRESHOLD = 120

# Tracking and cooldown windows
TRACKING_WINDOW_HOURS = 1
COOLDOWN_SECONDS = 3600

# Display formatting
MAX_DISPLAY_NAME_LENGTH = 22
LEADERBOARD_SEPARATOR_WIDTH = 34


class TouchGrass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activity = {}

    @commands.Cog.listener("on_message")
    async def on_message_activity(self, message: Message):
        """Monitor message activity and notify users who are too active."""
        await self.track_activity(message)

    async def track_activity(self, message: Message):
        """Track user message activity and send notification if threshold is reached."""
        if message.author.bot:
            return

        user_id = message.author.id
        now = utcnow()

        if user_id not in self.activity:
            self.activity[user_id] = {"messages": [], "last_notification": None}

        self.activity[user_id]["messages"].append(now)

        self.clean_old_messages(user_id, now)

        # Check if we should notify — lower threshold during work hours
        message_count = len(self.activity[user_id]["messages"])
        work_hours = self.is_work_hours(now)
        threshold = WORK_HOURS_THRESHOLD if work_hours else OFF_HOURS_THRESHOLD
        if message_count >= threshold and self.should_notify(user_id, now):
            await self.send_notification(message, message_count, work_hours)
            self.activity[user_id]["last_notification"] = now

    def is_work_hours(self, now) -> bool:
        """Check if current time is Mon-Fri 8am-6pm EDT (12pm-10pm UTC)."""
        return now.weekday() < 5 and 12 <= now.hour < 22

    def clean_old_messages(self, user_id: int, now):
        """Remove timestamps older than 60 minutes from the tracking window."""
        cutoff = now - datetime.timedelta(hours=TRACKING_WINDOW_HOURS)
        self.activity[user_id]["messages"] = [ts for ts in self.activity[user_id]["messages"] if ts > cutoff]

    def should_notify(self, user_id: int, now) -> bool:
        """Check if cooldown period has elapsed since last notification."""
        last_notif = self.activity[user_id].get("last_notification")
        if last_notif is None:
            return True
        return (now - last_notif).total_seconds() >= COOLDOWN_SECONDS

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

        for user_id in self.activity:
            self.clean_old_messages(user_id, now)

        stats = []
        for user_id, data in self.activity.items():
            count = len(data["messages"])
            if count > 0:
                stats.append((user_id, count))

        if not stats:
            await context.send(
                "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMmU1Mm0wZ2UxMW45MjR0M3I0dzVpaDVkajRpNDRyc2txd2xnZW13dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3OzmcOUXM3Kw0/giphy.gif"
            )
            return

        stats.sort(key=lambda x: x[1], reverse=True)

        lines = ["**Activity Leaderboard (Last 60 Minutes)**", "```"]
        lines.append(f"{'User':<24} {'Messages':>8}")
        lines.append("-" * LEADERBOARD_SEPARATOR_WIDTH)

        for user_id, count in stats:
            member = context.guild.get_member(user_id) if context.guild else None
            if member:
                name = member.display_name[:MAX_DISPLAY_NAME_LENGTH]
            else:
                user = self.bot.get_user(user_id)
                name = user.display_name[:MAX_DISPLAY_NAME_LENGTH] if user else f"User-{user_id}"

            lines.append(f"{name:<24} {count:>8}")

        lines.append("```")
        await context.send("\n".join(lines))
