import discord
import pytest


@pytest.fixture
def general_channel(bot, guild, text_channel) -> discord.TextChannel:
    """Modifies the `guild` and `text_channel` fixtures so that they have the expected values
    for the typical #general channel in the 'Friends Chat' discord server. Also, modifies the `bot` fixture
    so that the `get_all_channels` method returns the `text_channel`."""
    bot.get_all_channels.return_value = [text_channel]
    guild.name = "Friends Chat"
    text_channel.guild = guild
    text_channel.name = "general"
    return text_channel
