import discord
import pytest


@pytest.fixture(scope="session", autouse=True)
def patch_embed_str():
    """Monkeypatches in __str__ and __repr__ for discord.Embed, which does not provide any by default."""

    def embed_str(self: discord.Embed):
        return str(self.to_dict())

    discord.Embed.__str__ = embed_str
    discord.Embed.__repr__ = embed_str
    yield
