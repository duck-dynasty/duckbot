from discord.ext import commands
from discord import Embed, Colour
import random
import asyncio
from .eightball_phrases import phrases, joke_phrases


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eightball", aliases=["8ball"])
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
            if random.random() < 3.0 / 10.0:
                async with context.typing():
                    await asyncio.sleep(3.0)
                    await context.send(random.choice(joke_phrases))
            async with context.typing():
                await asyncio.sleep(5.0)
                await context.send(embed=Embed(colour=Colour.purple()).add_field(name=f"{context.author.display_name}, my :crystal_ball: says:", value=f"_{random.choice(phrases)}_"))
