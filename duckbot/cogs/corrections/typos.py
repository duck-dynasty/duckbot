from discord.ext import commands
from textblob import TextBlob


class Typos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def correct_typos(self, message):
        """Try to correct common typos for user's previous message."""
        if message.content.strip().lower() == "fuck":
            prev = await self.get_previous_message(message)
            if prev is not None:
                c = self.correct(prev.content)
                if c != prev.content:
                    await prev.reply(f"> {c}\nThink I fixed it, {message.author.display_name}!")
                else:
                    await message.reply(f"There's no need for harsh words, {message.author.display_name}.")

    def correct(self, sentence):
        return str(TextBlob(sentence).correct())

    async def get_previous_message(self, message):
        # limit of 20 may be restricting, since it includes everyone's messages
        hist = await message.channel.history(limit=20, before=message).flatten()
        by_same_author = list(x for x in hist if x.author.id == message.author.id)
        if not by_same_author:
            return None
        else:
            return by_same_author[0]
