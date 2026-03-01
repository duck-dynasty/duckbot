from typing import Optional, Union

import discord


async def get_user(bot, user_id: int, guild: Optional[discord.Guild] = None) -> Optional[Union[discord.Member, discord.User]]:
    """Returns the user with the given ID, checking cache first, then fetching via API if needed.
    Prefers returning a guild Member (which has server-specific display names) if a guild is provided.
    :param bot: the Discord bot
    :param user_id: the user ID to look up
    :param guild: optional guild to check for a member first"""
    if guild:
        return guild.get_member(user_id) or await guild.fetch_member(user_id)
    return bot.get_user(user_id) or await bot.fetch_user(user_id)
