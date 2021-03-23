import os
from discord.ext import commands


class Resources(commands.Cog, name="resources"):
    """Provides access to resource files."""

    def __init__(self, bot):
        self.bot = bot

    def get(self, path, *paths):
        """Returns the path to a resources file. `path` and `paths` are joined via `os.path.join`
        to form a complete path to the resource file.
        raises FileNotFoundError: when the resource does not exist"""
        base_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources")
        resource = os.path.join(base_path, path, *paths)
        if os.path.exists(resource):
            return os.path.abspath(resource)
        else:
            raise FileNotFoundError(resource)
