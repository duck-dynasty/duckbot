from discord import Member, User


class Interaction:
    """https://discord.com/developers/docs/interactions/slash-commands#interaction"""

    def __init__(self, *, bot, data):
        print(data)
        self.bot = bot
        self.id = int(data["id"])
        self.application_id = int(data["application_id"])
        self.token = data["token"]
        self.channel = bot.get_channel(data["channel_id"])
        self.data = data["data"]
        if "guild_id" in data:
            self.guild = bot.get_guild(data["guild_id"])
            self.author = Member(data=data["member"], guild=self.guild, state=bot._connection)
        else:
            self.guild = None
            self.author = User(data=data["user"], state=bot._connection)
