from typing import Optional, Union

from discord import Client, Guild, Member, User
from discord.abc import GuildChannel, PrivateChannel


class Interaction:
    """https://discord.com/developers/docs/interactions/slash-commands#interaction"""

    def __init__(self, *, bot: Client, data):
        self.bot = bot
        self.raw_data = data

    @property
    def id(self) -> int:
        return int(self.raw_data["id"])

    @property
    def application_id(self) -> int:
        return int(self.raw_data["application_id"])

    @property
    def token(self) -> str:
        return self.raw_data["token"]

    @property
    def channel(self) -> Optional[Union[GuildChannel, PrivateChannel]]:
        return self.bot.get_channel(self.raw_data["channel_id"])

    @property
    def guild(self) -> Optional[Guild]:
        return self.bot.get_guild(self.raw_data["guild_id"]) if "guild_id" in self.raw_data else None

    @property
    def author(self) -> Union[Member, User]:
        if "guild_id" in self.raw_data:
            return Member(data=self.raw_data["member"], guild=self.guild, state=self.bot._connection)
        else:
            return User(data=self.raw_data["user"], state=self.bot._connection)

    @property
    def data(self):
        return self.raw_data["data"]

    def __eq__(self, other):
        return self.raw_data == other.raw_data if isinstance(other, Interaction) else False

    def __str__(self):
        return str(self.raw_data)

    def __repr__(self):
        return str(self.raw_data)
