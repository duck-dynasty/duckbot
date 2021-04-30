import pytest
from unittest import mock
import discord
from discord.ext.commands import Bot, Context
from discord import TextChannel, VoiceChannel, Guild, Emoji, Message, VoiceClient


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


@pytest.fixture
async def message() -> Message:
    return patch_of("discord.Message")


@pytest.fixture
async def context() -> Context:
    return patch_of("discord.ext.commands.Context")


@pytest.fixture
async def emoji() -> Emoji:
    return patch_of("discord.Emoji")


@pytest.fixture
async def guild() -> Guild:
    return patch_of("discord.Guild")


@pytest.fixture
async def message() -> Message:
    return patch_of("discord.Message")


@pytest.fixture
async def channel(text_channel) -> TextChannel:
    return text_channel


@pytest.fixture
@mock.patch("discord.TextChannel", autospec=True)
async def text_channel(tex) -> TextChannel:
    tex.type = discord.ChannelType.text
    return tex


@pytest.fixture
@mock.patch("discord.DMChannel", autospec=True)
async def dm_channel(dm) -> discord.DMChannel:
    dm.type = discord.ChannelType.private
    return dm


@pytest.fixture
async def voice_channel() -> VoiceChannel:
    return patch_of("discord.VoiceChannel")


@pytest.fixture
async def voice_client() -> VoiceClient:
    return patch_of("discord.VoiceClient")


def patch_of(tpye):
    with mock.patch(tpye) as o:
        return o
