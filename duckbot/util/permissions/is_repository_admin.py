from discord.ext import commands

REPOSITORY_ADMINS = (368038054558171141, 776607982472921088, 375024417358479380)


async def is_repository_admin(context: commands.Context):
    """Command check: server-only, and only the bot owner or a repository owner."""
    if context.guild is None:
        raise commands.NoPrivateMessage()
    if not await context.bot.is_owner(context.author) and context.author.id not in REPOSITORY_ADMINS:
        raise commands.MissingPermissions(["repository admin"])
    return True
