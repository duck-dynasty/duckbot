from discord import Forbidden, ForumChannel, Guild, TextChannel
from discord.abc import Messageable


async def channels_and_threads(guild: Guild):
    """Yields every channel in the guild that holds messages, plus active and archived threads."""
    for channel in guild.channels:
        if isinstance(channel, Messageable):
            yield channel
        if isinstance(channel, (TextChannel, ForumChannel)):
            for thread in channel.threads:
                yield thread
            try:
                async for thread in channel.archived_threads(limit=None):
                    yield thread
            except Forbidden:
                pass
