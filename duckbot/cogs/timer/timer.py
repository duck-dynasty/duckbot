import asyncio
import datetime
import re

from discord.ext import commands

from duckbot.util.datetime import now

DURATION_PATTERN = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")


def parse_duration(duration: str) -> datetime.timedelta:
    """Parses strings like 1h30m, 90s, or bare minutes into a timedelta; None if invalid."""
    if duration.isdigit():
        delta = datetime.timedelta(minutes=int(duration))
    else:
        match = DURATION_PATTERN.fullmatch(duration.lower())
        if match and any(match.groups()):
            hours, minutes, seconds = (int(g or 0) for g in match.groups())
            delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
        else:
            delta = None
    return delta


class Timer(commands.Cog):
    @commands.hybrid_command(name="timer", description="Set a timer; get pinged when it ends.")
    async def timer(self, context: commands.Context, duration: str, *, label: str = None):
        """
        :param duration: How long, eg 10, 90s, 1h30m.
        :param label: What the timer is for.
        """
        delta = parse_duration(duration)
        if delta is None or delta.total_seconds() <= 0:
            await context.send("I can't count that. Try something like `10`, `90s` or `1h30m`.")
        else:
            bedtime = now().replace(hour=23, minute=50, second=0, microsecond=0)
            if now() + delta > bedtime:
                await context.send("I'm asleep by then... screw flanders.")
            else:
                await context.send(f":timer: Timer set for {duration}. If I die before then, you're on your own.")
                await asyncio.sleep(delta.total_seconds())
                name = f"{label} timer" if label else "timer"
                await context.channel.send(f":alarm_clock: {context.author.mention} your {name} is up!")
