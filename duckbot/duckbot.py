from discord import Intents, Game
from discord.ext import commands


def intents() -> Intents:
    intent = Intents.default()
    intent.members = False
    intent.presences = False
    intent.bans = False
    intent.integrations = False
    intent.webhooks = False
    intent.invites = False
    intent.webhooks = False
    intent.typing = False
    return intent


class DuckBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", help_command=None, intents=intents(), activity=Game(name="Duck Game"))
        self.add_listener(self.ready, name="on_ready")

    async def ready(self):
        print("DuckBot online")
