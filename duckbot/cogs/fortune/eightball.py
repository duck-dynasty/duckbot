import asyncio
import random

from discord import Colour, Embed
from discord.ext import commands

from duckbot.slash import Option, slash_command

from .eightball_phrases import joke_phrases, phrases


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(options=[Option(name="question", description="The question to ask the magic 8 ball.")])
    @commands.command(name="eightball", aliases=["8ball"], description="Ask the magic 8 ball a question!")
    async def eightball_command(self, context, *, question: str = None):
        await self.eightball(context, question)

    async def eightball(self, context: commands.Context, question: str):
        if question is None:
            await context.send("You need to ask a question to get an answer. :unamused:")
        elif len(question.replace("?", "")) == 0:
            await context.send("Who do you think you are? I AM!\nhttps://youtu.be/gKQOXYB2cd8?t=10")
        elif not question.endswith("?"):
            await context.send("I can't tell if that's a question, brother.")
        else:
            async with context.typing():
                if random.random() < 3.0 / 10.0:
                    await asyncio.sleep(3.0)
                    await context.send(random.choice(joke_phrases))
                await asyncio.sleep(5.0)
                await context.send(embed=Embed(colour=Colour.purple()).add_field(name=f"{context.author.display_name}, my :crystal_ball: says:", value=f"_{random.choice(phrases)}_"))
