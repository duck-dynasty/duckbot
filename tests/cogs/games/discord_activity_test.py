from unittest import mock

import discord
import pytest

from duckbot.cogs.games import DiscordActivity


@pytest.mark.asyncio
async def test_before_loop_waits_for_bot(bot):
    clazz = DiscordActivity(bot)
    await clazz.before_loop()
    bot.wait_until_ready.assert_called()


@pytest.mark.asyncio
async def test_cog_unload_cancels_task(bot):
    clazz = DiscordActivity(bot)
    clazz.cog_unload()
    clazz.change_activity_loop.cancel.assert_called()


@pytest.mark.asyncio
@mock.patch("random.choice", return_value=discord.Game("game"))
async def test_change_activity_changes_activity(choice, bot):
    clazz = DiscordActivity(bot)
    await clazz.change_activity()
    bot.change_presence.assert_called_once_with(activity=discord.Game("game"))
