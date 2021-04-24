import pytest
import mock
import discord
import discord.ext.commands


@pytest.fixture(autouse=True)
def async_mock_await_fix():
    """Make it so @mock.patch works for async methods."""

    async def async_magic():
        """This method's __await__ is used to hack mock awaits. No implementation needed."""
        pass

    mock.MagicMock.__await__ = lambda x: async_magic().__await__()
    yield


@pytest.fixture
async def bot_spy() -> discord.ext.commands.Bot:
    """Returns a spy discord.ext.commands.Bot instance with a stubbed `run` method. The bot is closed afterwards."""
    b = mock.Mock(wraps=discord.ext.commands.Bot(command_prefix="!", help_command=None))
    with mock.patch.object(discord.ext.commands.Bot, "run"):  # stub run so it does nothing
        yield b
    await b.close()


@pytest.fixture
@mock.patch("discord.ext.commands.Bot")
async def bot(b) -> discord.ext.commands.Bot:
    return b


@pytest.fixture
@mock.patch("discord.Message")
async def message(m) -> discord.Message:
    return m


@pytest.fixture
@mock.patch("discord.ext.commands.Context")
async def context(c) -> discord.ext.commands.Context:
    return c


@pytest.fixture
@mock.patch("discord.Emoji")
async def emoji(e) -> discord.Emoji:
    return e


@pytest.fixture
@mock.patch("discord.Guild")
async def guild(g) -> discord.Guild:
    return g


@pytest.fixture
async def channel(text_channel) -> discord.TextChannel:
    return text_channel


@pytest.fixture
@mock.patch("discord.TextChannel")
async def text_channel(tc) -> discord.TextChannel:
    return tc


@pytest.fixture
@mock.patch("discord.VoiceChannel")
async def voice_channel(vc) -> discord.VoiceChannel:
    return vc


@pytest.fixture
@mock.patch("discord.VoiceClient")
async def voice_client(vc) -> discord.VoiceClient:
    return vc
