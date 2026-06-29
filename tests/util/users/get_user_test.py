from unittest import mock

import discord

from duckbot.util.users import get_user


async def test_get_user_guild_member_in_cache(bot, guild, member):
    guild.get_member.return_value = member
    result = await get_user(bot, 123, guild)
    assert result is member
    guild.fetch_member.assert_not_called()


async def test_get_user_guild_member_not_in_cache(bot, guild, member):
    guild.get_member.return_value = None
    guild.fetch_member.return_value = member
    result = await get_user(bot, 123, guild)
    assert result is member
    guild.fetch_member.assert_called_once_with(123)


async def test_get_user_no_guild_user_in_cache(bot, user):
    bot.get_user.return_value = user
    result = await get_user(bot, 123)
    assert result is user
    bot.fetch_user.assert_not_called()


async def test_get_user_no_guild_user_not_in_cache(bot, user):
    bot.get_user.return_value = None
    bot.fetch_user.return_value = user
    result = await get_user(bot, 123)
    assert result is user
    bot.fetch_user.assert_called_once_with(123)


async def test_get_user_guild_member_left(bot, guild):
    guild.get_member.return_value = None
    guild.fetch_member.side_effect = discord.NotFound(mock.Mock(status=404), "unknown member")
    assert await get_user(bot, 123, guild) is None


async def test_get_user_no_guild_user_not_found(bot):
    bot.get_user.return_value = None
    bot.fetch_user.side_effect = discord.NotFound(mock.Mock(status=404), "unknown user")
    assert await get_user(bot, 123) is None
