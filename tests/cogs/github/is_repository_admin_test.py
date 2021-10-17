from unittest import mock

import pytest
from discord.ext import commands

from duckbot.cogs.github.yolo_merge import is_repository_admin


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Context")
async def test_is_repository_admin_not_in_guild(context):
    context.guild = None
    with pytest.raises(commands.NoPrivateMessage):
        await is_repository_admin(context)


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Context")
async def test_is_repository_admin_not_bot_owner_or_repo_admin(context, guild, bot, user):
    context.guild = guild
    context.bot = bot
    context.author = user
    user.id = 0  # not a repo admin
    bot.is_owner.return_value = False
    with pytest.raises(commands.MissingPermissions):
        await is_repository_admin(context)
    bot.is_owner.assert_called_once_with(user)


@pytest.mark.asyncio
@pytest.mark.parametrize("admin", [368038054558171141, 776607982472921088, 375024417358479380])
@mock.patch("discord.ext.commands.Context")
async def test_is_repository_admin_repo_admin(context, guild, bot, user, admin):
    context.guild = guild
    context.bot = bot
    context.author = user
    user.id = admin
    bot.is_owner.return_value = False
    assert await is_repository_admin(context) is True
    bot.is_owner.assert_called_once_with(user)


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Context")
async def test_is_repository_admin_bot_owner(context, guild, bot, user):
    context.guild = guild
    context.bot = bot
    context.author = user
    user.id = 0
    bot.is_owner.return_value = True
    assert await is_repository_admin(context) is True
    bot.is_owner.assert_called_once_with(user)
