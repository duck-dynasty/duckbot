import mock
from duckbot.cogs import Fortune


@mock.patch("discord.ext.commands.Bot")
def test_get_fortune(bot):
    clazz = Fortune(bot)
    message = clazz.get_fortune()
    assert message.startswith("```")
    assert message.endswith("```")
    assert len(message) < 2000
