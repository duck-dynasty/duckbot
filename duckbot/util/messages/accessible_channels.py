from discord import Forbidden, Guild


async def accessible_channels(guild: Guild):
    """Yields every text channel and thread in the guild whose message history the bot can read."""
    for channel in guild.text_channels:
        if not channel.permissions_for(guild.me).read_message_history:
            continue
        yield channel
        for thread in channel.threads:
            yield thread
        try:
            async for thread in channel.archived_threads(limit=None):
                yield thread
        except Forbidden:
            pass
