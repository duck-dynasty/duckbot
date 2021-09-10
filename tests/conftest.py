import logging
from unittest import mock

import discord
import discord.ext.commands
import discord.ext.tasks
import pytest

from duckbot import DuckBot


def pytest_configure(config):
    # flake8 logs a ton, suppress it
    logging.getLogger("flake8").setLevel(logging.ERROR)


@pytest.fixture(scope="session", autouse=True)
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
@mock.patch("duckbot.DuckBot", autospec=True)
def bot(b, monkeypatch) -> DuckBot:
    """Returns a mock DuckBot instance. The default event loops are replaced by mocks."""
    b.loop = mock.Mock()
    monkeypatch.setattr(discord.ext.tasks, "Loop", mock.Mock())  # mock out loop, it uses `asyncio.get_event_loop()` by default
    return b


@pytest.fixture
@mock.patch("discord.User", autospec=True)
def user(u) -> discord.User:
    """Returns a mock discord User, someone in a private channel (eg DM)."""
    return u


@pytest.fixture
@mock.patch("discord.Member", autospec=True)
def member(m) -> discord.Member:
    """Returns a mock discord Member, someone in a discord server."""
    return m


@pytest.fixture
@mock.patch("discord.Message", autospec=True)
def message(m, channel, user, member) -> discord.Message:
    """Returns a message with nested properties set, for each channel type a message can be sent to."""
    m.channel = channel
    m.author = user if channel.type in [discord.ChannelType.private, discord.ChannelType.group] else member
    return m


@pytest.fixture
@mock.patch("discord.ext.commands.Context", autospec=True)
def context(c, message) -> discord.ext.commands.Context:
    """Returns a context with nested properties set, for each channel type a command can be sent to."""
    c.message = message
    c.channel = message.channel
    c.author = message.author
    return c


@pytest.fixture
@mock.patch("discord.Emoji", autospec=True)
def emoji(e) -> discord.Emoji:
    """Returns a mock Emoji."""
    return e


@pytest.fixture
@mock.patch("discord.Guild", autospec=True)
def guild(g) -> discord.Guild:
    """Returns a mock Guild, ie a discord server."""
    return g


@pytest.fixture(params=["discord.TextChannel", "discord.DMChannel", "discord.GroupChannel", "discord.Thread"])
def channel(request, text_channel, dm_channel, group_channel, thread):
    """Returns a text based channel."""
    if request.param == "discord.TextChannel":
        return text_channel
    elif request.param == "discord.DMChannel":
        return dm_channel
    elif request.param == "discord.GroupChannel":
        return group_channel
    elif request.param == "discord.Thread":
        return thread
    raise AssertionError


@pytest.fixture
def skip_if_private_channel(channel, dm_channel, group_channel):
    if channel is dm_channel or channel is group_channel:
        pytest.skip("test requires a non-private discord channel")


@pytest.fixture
@mock.patch("discord.TextChannel", autospec=True)
def text_channel(tc) -> discord.TextChannel:
    """Returns a text channel, a typical channel in a discord server."""
    tc.type = discord.ChannelType.text
    return tc


@pytest.fixture
@mock.patch("discord.DMChannel", autospec=True)
def dm_channel(dm) -> discord.DMChannel:
    """Returns a dm channel, a direct message between two users."""
    dm.type = discord.ChannelType.private
    return dm


@pytest.fixture
@mock.patch("discord.GroupChannel", autospec=True)
def group_channel(g) -> discord.GroupChannel:
    """Returns a group channel, a private channel between two or more users, outside of a server."""
    g.type = discord.ChannelType.group
    return g


@pytest.fixture
@mock.patch("discord.Thread", autospec=True)
def thread(thrd) -> discord.Thread:
    """Returns a thread channel, an ephemeral channel inside of a discord server."""
    thrd.type = discord.ChannelType.public_thread
    return thrd


@pytest.fixture
@mock.patch("discord.VoiceChannel", autospec=True)
def voice_channel(vc) -> discord.VoiceChannel:
    """Returns a voice channel, an audio only channel in a discord server."""
    vc.type = discord.ChannelType.voice
    return vc


@pytest.fixture
@mock.patch("discord.VoiceClient", autospec=True)
def voice_client(vc) -> discord.VoiceClient:
    """Returns a mock voice client."""
    return vc


@pytest.fixture(scope="session", autouse=True)
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
