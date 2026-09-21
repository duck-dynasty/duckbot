from discord import Forbidden, ForumChannel, Guild, TextChannel
from discord.abc import Messageable


async def accessible_channels(guild: Guild):
    """Yields every channel and thread in the guild whose message history the bot can read."""
    for channel in guild.channels:
        if not channel.permissions_for(guild.me).read_message_history:
            continue
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
