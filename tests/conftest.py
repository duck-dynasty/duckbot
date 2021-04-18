import pytest
import mock
from discord.ext.commands import Bot
from discord import TextChannel, Guild, Emoji


@pytest.fixture(autouse=True)
def async_mock_await_fix():
    """Make it so @mock.patch works for async methods."""

    async def async_magic():
        """This method's __await__ is used to hack mock awaits. No implementation needed."""
        pass

    mock.MagicMock.__await__ = lambda x: async_magic().__await__()
    yield


@pytest.fixture
async def bot_spy() -> Bot:
    """Returns a spy discord.ext.commands.Bot instance with a stubbed `run` method. The bot is closed afterwards."""
    b = mock.Mock(wraps=Bot(command_prefix="!", help_command=None))
    with mock.patch.object(Bot, "run"):  # stub run so it does nothing
        yield b
    await b.close()


@pytest.fixture
async def bot() -> Bot:
    return patch_of("discord.ext.commands.Bot")


def patch_of(tpye):
    with mock.patch(tpye) as o:
        return o
