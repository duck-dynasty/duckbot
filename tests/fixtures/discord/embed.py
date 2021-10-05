import discord
import pytest


@pytest.fixture(scope="session", autouse=True)
def patch_embed_equals():
    """Replaces discord.Embed equality test with comparing the `to_dict` of each side.
    This allows for writing `context.send.assert_called_once_with(embed=expected)`,
    as discord.Embed doesn't implement equals itself.
    See also: https://github.com/Rapptz/discord.py/issues/5962"""

    def embed_equals(self: discord.Embed, other: discord.Embed):
        return self.to_dict() == other.to_dict()

    def embed_str(self: discord.Embed):
        return str(self.to_dict())

    discord.Embed.__eq__ = embed_equals
    discord.Embed.__str__ = embed_str
    discord.Embed.__repr__ = embed_str
    yield
