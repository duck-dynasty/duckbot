import os
import re

import discord
import groq
from discord.ext import commands

from duckbot.cogs.ai.groq_api import complete
from duckbot.util.messages import get_message_reference

EXPLAIN_PROMPT = """Someone on our Discord server replied "what?" to a message from {user_name} because they didn't understand it.

Recent conversation, oldest first:
{conversation}

Message to explain, from {user_name}:
"{user_message}"

Explain in plain language what {user_name} meant. Unpack any slang, nicknames, references or jargon. Use the conversation only as context.
Keep it to a few short sentences, formatted with Discord-friendly markdown."""


class Explain(commands.Cog):
    def __init__(self):
        self._ai_client = None

    @property
    def ai_client(self):
        if self._ai_client is None:
            self._ai_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self._ai_client

    @commands.Cog.listener("on_message")
    async def explain_on_what(self, message: discord.Message):
        if not message.author.bot and re.fullmatch(r"(what|wut|wat|whut|wha|wuh|huh)[?!]*", message.content.strip(), re.IGNORECASE):
            referenced_message = await get_message_reference(message)
            if referenced_message:
                async with message.channel.typing():
                    await message.reply(await self.explain(referenced_message))

    async def explain(self, message: discord.Message) -> str:
        history = [m async for m in message.channel.history(limit=5, before=message)]
        conversation = "\n".join(f"{m.author.display_name}: {m.clean_content}" for m in reversed(history))
        prompt = EXPLAIN_PROMPT.format(user_name=message.author.display_name, user_message=message.clean_content, conversation=conversation)
        return complete(self.ai_client, prompt)
