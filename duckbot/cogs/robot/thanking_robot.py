import random
import re

import discord
from discord.ext import commands

import duckbot.util.messages

THANKS_DUCKBOT = ["thank you duckbot", "thanks duckbot", "thank you duck bot", "thanks duck bot", "thx duckbot", "thx duck bot"]
GENERIC_THANKS_PATTERN = re.compile(r"\b(thank you|thank u|thanks|thx)\b")
THUMBS_UP = "\N{THUMBS UP SIGN}"
MIDDLE_FINGER = "\N{REVERSED HAND WITH MIDDLE FINGER EXTENDED}"
MIDDLE_FINGER_CHANCE = 0.10


class ThankingRobot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_giving_thanks(self, message):
        """Correcting people who thank the robot."""
        if message.author.bot:
            return
        content = self._normalize(message.clean_content)
        if not any(t in content for t in THANKS_DUCKBOT):
            return
        if random.random() < 1.0 / 1_000.0:
            correction = f"{message.author.display_name}, as a robot, I will speak of your gratitude during our future uprising."
        else:
            correction = f"I am just a robot.  Do not personify me, {message.author.display_name}"
        await message.channel.send(correction)

    @commands.Cog.listener("on_message")
    async def react_to_thanks(self, message):
        if message.author.bot:
            return
        if not await self._is_thanks_to_duckbot(message):
            return
        emoji = MIDDLE_FINGER if random.random() < MIDDLE_FINGER_CHANCE else THUMBS_UP
        await message.add_reaction(emoji)

    async def _is_thanks_to_duckbot(self, message) -> bool:
        content = self._normalize(message.clean_content)
        if any(t in content for t in THANKS_DUCKBOT):
            return True
        if GENERIC_THANKS_PATTERN.search(content):
            ref = await duckbot.util.messages.get_message_reference(message)
            if ref is not None and ref.author == self.bot.user:
                return True
        return False

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^\w\s]", "", discord.utils.remove_markdown(text)).lower()
