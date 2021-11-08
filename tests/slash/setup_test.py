from duckbot.slash import SlashCommandHandler
from duckbot.slash import setup as extension_setup
from tests.discord_test_ext import assert_cog_added_of_type


def test_setup(bot_spy):
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, SlashCommandHandler)
