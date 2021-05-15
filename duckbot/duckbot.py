from discord import Game, Intents
from discord.ext import commands

import duckbot.slash


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
        self.load_extension(duckbot.slash.__name__)

    async def ready(self):
        print("DuckBot online")
