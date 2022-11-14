from discord import Intents
from discord.ext import commands


def intents() -> Intents:
    intent = Intents.none()
    intent.guilds = True
    intent.emojis = True
    intent.messages = True
    intent.message_content = True
    intent.reactions = True
    intent.voice_states = True
    return intent


class DuckBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", help_command=None, intents=intents())

    async def setup_hook(self):
        print("DuckBot online")
