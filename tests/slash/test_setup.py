from tests.discord_test_ext import assert_cog_added_of_type
from duckbot.slash import setup as extension_setup
from duckbot.slash.core import SlashCommandPatch


def test_setup(bot_spy):
    bot_spy._connection.parsers = {}  # mock doesn't allow assignment, so make it a real object
    extension_setup(bot_spy)
    assert_cog_added_of_type(bot_spy, SlashCommandPatch)
