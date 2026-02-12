import pytest

from duckbot.health import HealthCheck
from duckbot.util.connection_test import ConnectionTest


@pytest.fixture
def health_cog(autospec, bot):
    cog = autospec.of(HealthCheck)
    bot.get_cog.return_value = cog
    return cog


async def test_connection_success_shuts_down_bot_when_sanity_passes(bot, health_cog):
    health_cog.sanity_check.return_value = True
    clazz = ConnectionTest(bot)
    await clazz.connection_success()
    bot.get_cog.assert_called_with(HealthCheck.__cog_name__)
    health_cog.sanity_check.assert_called_once()
    bot.close.assert_called()


async def test_connection_success_raises_when_sanity_fails(bot, health_cog):
    health_cog.sanity_check.return_value = False
    clazz = ConnectionTest(bot)
    with pytest.raises(RuntimeError, match="Sanity check failed"):
        await clazz.connection_success()


async def test_connection_success_raises_when_health_cog_missing(bot):
    bot.get_cog.return_value = None
    clazz = ConnectionTest(bot)
    with pytest.raises(RuntimeError, match="Sanity check failed"):
        await clazz.connection_success()
