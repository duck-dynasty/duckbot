import os
from discord.ext import commands


class Resources(commands.Cog, name="resources"):
    """Provides access to resource files."""

    def __init__(self, bot):
        self.bot = bot

    def get(self, *args):
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources")
        resource = os.path.join(base_path, *args)
        if os.path.exists(resource):
            return resource
        else:
            raise FileNotFoundError(resource)
