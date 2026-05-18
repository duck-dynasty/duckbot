import random
import re

import discord
from discord.ext import commands

from duckbot.util.messages import get_message_reference

THANKS_DUCKBOT = ["thank you duckbot", "thanks duckbot", "thank you duck bot", "thanks duck bot", "thx duckbot", "thx duck bot"]
GENERIC_THANKS_PATTERN = re.compile(r"\b(thank you|thank u|thanks|thx)\b")
MIDDLE_FINGER_CHANCE = 0.10


class ThankingRobot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_giving_thanks(self, message):
        """Correcting people who thank the robot."""
        if message.author.bot:
            return
        content = re.sub(r"[^\w\s]", "", discord.utils.remove_markdown(message.clean_content)).lower()
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
        content = re.sub(r"[^\w\s]", "", discord.utils.remove_markdown(message.clean_content)).lower()
        if not any(t in content for t in THANKS_DUCKBOT):
            if not GENERIC_THANKS_PATTERN.search(content):
                return
            ref = await get_message_reference(message)
            if ref is None or ref.author != self.bot.user:
                return
        emoji = "\N{REVERSED HAND WITH MIDDLE FINGER EXTENDED}" if random.random() < MIDDLE_FINGER_CHANCE else "\N{THUMBS UP SIGN}"
        await message.add_reaction(emoji)
