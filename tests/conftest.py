from unittest import mock

import discord
import discord.ext.commands
import pytest

from duckbot import DuckBot


@pytest.fixture(autouse=True)
def async_mock_await_fix():
    """Make it so @mock.patch works for async methods."""

    async def async_magic():
        """This method's __await__ is used to hack mock awaits. No implementation needed."""
        pass

    mock.MagicMock.__await__ = lambda x: async_magic().__await__()
    yield


@pytest.fixture
@mock.patch("sqlalchemy.orm.session.Session")
def session(s):
    return s


@pytest.fixture
@mock.patch("duckbot.db.Database")
def db(d, session):
    """Returns a database with a stubbed session value."""
    d.session.return_value.__enter__.return_value = session
    return d


@pytest.fixture
async def bot_spy() -> DuckBot:
    """Returns a spy DuckBot instance with a stubbed `run` method. The bot is closed afterwards."""
    b = DuckBot()
    m = mock.Mock(wraps=b)
    m.loop = b.loop
    with mock.patch.object(DuckBot, "run"):  # stub run so it does nothing
        yield m
    await b.close()


@pytest.fixture
@mock.patch("duckbot.DuckBot")
async def bot(b) -> DuckBot:
    return b


@pytest.fixture
@mock.patch("discord.Message", autospec=True)
async def message(m, channel) -> discord.Message:
    """Returns a message with the channel property set, for each channel type a message can be sent to."""
    m.channel = channel
    return m


@pytest.fixture
@mock.patch("discord.Message", autospec=True)
async def text_message(m, text_channel) -> discord.Message:
    """Returns a guild TextChannel message with the channel property set."""
    m.channel = text_channel
    return m


@pytest.fixture
@mock.patch("discord.ext.commands.Context")
async def context(c, message) -> discord.ext.commands.Context:
    """Returns a context with the message and channel properties set, for each channel type a command can be sent to."""
    c.message = message
    c.channel = message.channel
    return c


@pytest.fixture
@mock.patch("discord.Emoji", autospec=True)
async def emoji(e) -> discord.Emoji:
    return e


@pytest.fixture
@mock.patch("discord.Guild", autospec=True)
async def guild(g) -> discord.Guild:
    return g


@pytest.fixture(params=["discord.TextChannel", "discord.VoiceChannel"])
async def guild_channel(request, text_channel, voice_channel):
    """Returns a guild TextChannel and a VoiceChannel."""
    if request.param == "discord.TextChannel":
        return text_channel
    elif request.param == "discord.VoiceChannel":
        return voice_channel
    raise AssertionError


@pytest.fixture(params=["discord.TextChannel", "discord.DMChannel", "discord.GroupChannel"])
async def channel(request, text_channel, dm_channel, group_channel):
    """Returns a text based channel."""
    if request.param == "discord.TextChannel":
        return text_channel
    elif request.param == "discord.DMChannel":
        return dm_channel
    elif request.param == "discord.GroupChannel":
        return group_channel
    raise AssertionError


@pytest.fixture
@mock.patch("discord.TextChannel", autospec=True)
async def text_channel(tc) -> discord.TextChannel:
    tc.type = discord.ChannelType.text
    return tc


@pytest.fixture
@mock.patch("discord.DMChannel", autospec=True)
async def dm_channel(dm) -> discord.DMChannel:
    dm.type = discord.ChannelType.private
    return dm


@pytest.fixture
@mock.patch("discord.GroupChannel", autospec=True)
async def group_channel(g) -> discord.GroupChannel:
    g.type = discord.ChannelType.group
    return g


@pytest.fixture
@mock.patch("discord.VoiceChannel", autospec=True)
async def voice_channel(vc) -> discord.VoiceChannel:
    vc.type = discord.ChannelType.voice
    return vc


@pytest.fixture
@mock.patch("discord.VoiceClient", autospec=True)
async def voice_client(vc) -> discord.VoiceClient:
    return vc


@pytest.fixture(autouse=True)
def patch_embed_equals():
    """Replaces discord.Embed equality test with comparing the `to_dict` of each side.
    This allows for writing `context.send.assert_called_once_with(embed=expected)`,
    as discord.Embed doesn't implement equals itself.
    See also: https://github.com/Rapptz/discord.py/issues/5962"""

    def embed_equals(self, other):
        return self.to_dict() == other.to_dict()

    def embed_str(self):
        return str(self.to_dict())

    discord.Embed.__eq__ = embed_equals
    discord.Embed.__str__ = embed_str
    discord.Embed.__repr__ = embed_str
    yield
