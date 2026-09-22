from datetime import timedelta

from discord import Embed, Forbidden, Guild, Message
from discord.ext import commands

from duckbot.util.datetime import now
from duckbot.util.messages import accessible_channels


class EmojiUsage(commands.Cog):
    @commands.command(name="emoji-usage")
    @commands.guild_only()
    async def emoji_usage(self, context, days: int = 90):
        async with context.typing():
            counts = await self.gather_counts(context.guild, days)
            await context.send(embed=self.report(counts, days))

    async def gather_counts(self, guild: Guild, days: int):
        counts = {emoji: 0 for emoji in guild.emojis}
        after = now() - timedelta(days=days)
        async for channel in accessible_channels(guild):
            try:
                async for message in channel.history(limit=None, after=after):
                    self.tally(counts, message)
            except Forbidden:
                pass
        return counts

    def tally(self, counts, message: Message):
        for emoji in counts:
            counts[emoji] += message.content.count(str(emoji))
        for reaction in message.reactions:
            if reaction.emoji in counts:
                counts[reaction.emoji] += reaction.count

    def report(self, counts, days: int) -> Embed:
        ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0].name))
        return Embed(title=f"Emoji Usage \N{MIDDLE DOT} last {days} days", description="\n".join(f"{emoji} {count}" for emoji, count in ranked))
