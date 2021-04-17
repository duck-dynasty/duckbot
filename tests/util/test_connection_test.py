import pytest
import mock
from duckbot.util import ConnectionTest


@pytest.mark.asyncio
@mock.patch("discord.ext.commands.Bot")
@mock.patch("asyncio.AbstractEventLoop")
async def test_connection_success_shuts_down_bot(bot, loop):
    bot.loop = loop
    clazz = ConnectionTest(bot)
    await clazz.connection_success()
    bot.close.assert_called()
