import asyncio
from importlib.resources import path

import discord
import nltk
from discord.ext import commands


class HealthCheck(commands.Cog):
    REQUIRED_CORPORA = [
        "corpora/cmudict",  # haiku detection
        "corpora/brown",  # textblob
        "tokenizers/punkt_tab",  # textblob
        "corpora/wordnet.zip",  # textblob
        "taggers/averaged_perceptron_tagger_eng",  # textblob
        "corpora/conll2000",  # textblob
        "corpora/movie_reviews",  # textblob
    ]
    REQUIRED_RESOURCES = ["10am-mfer.png", "who-can-it-be-now.mp3"]

    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def start_health_check_tasks(self):
        await asyncio.start_server(self.healthcheck, host="127.0.0.1", port=8008)

    def healthcheck(self, reader, writer):
        if self.bot.user is None or not self.bot.is_ready() or self.bot.is_closed() or self.bot.latency > 1.0 or not self.sanity_check():
            writer.write(b"unhealthy")
        else:
            writer.write(b"healthy")
        writer.close()

    def sanity_check(self):
        """Verify that all runtime dependencies are properly installed."""
        try:
            for corpus in self.REQUIRED_CORPORA:
                nltk.data.find(corpus)
            for resource in self.REQUIRED_RESOURCES:
                with path("resources", resource) as p:
                    if not p.exists():
                        return False
            return True
        except LookupError:
            return False
