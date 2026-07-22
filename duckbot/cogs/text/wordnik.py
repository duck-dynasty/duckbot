import html
import os
import re
from typing import List

import discord
import requests
from discord.ext import commands

from duckbot.util.embeds import MAX_FIELD_VALUE_LENGTH

SOURCE_DICTIONARIES = ["ahd-5", "wiktionary", "century", "wordnet"]


class Wordnik(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://api.wordnik.com/v4/word.json"
        self.api_key = os.getenv("WORDNIK_KEY")

    @commands.hybrid_command(name="define", description="Define a brother, word.")
    async def define(self, context: commands.Context, *, word: str = "taco"):
        """
        :param word: The word to define.
        """
        async with context.typing():
            definitions = self.get_definitions(word.lower()) or self.get_definitions("why")
            if definitions:
                await context.send(embed=self.get_embed(definitions))
            else:
                await context.send("wordnik is all worded out, give it a minute")

    def get_definitions(self, word: str) -> List[dict]:
        """Returns definitions from the most preferred source dictionary that has any; inflections resolve to their root word."""
        params = {"api_key": self.api_key, "useCanonical": "true", "sourceDictionaries": ",".join(SOURCE_DICTIONARIES), "limit": 10}
        response = requests.get(f"{self.url}/{word}/definitions", params=params, timeout=(3.05, 27)).json()
        return [d for d in response if d.get("text")] if isinstance(response, list) else []

    def get_pronunciation(self, word: str) -> str:
        response = requests.get(f"{self.url}/{word}/pronunciations", params={"api_key": self.api_key, "limit": 10}, timeout=(3.05, 27)).json()
        pronunciations = response if isinstance(response, list) else []
        ranked = sorted((p for p in pronunciations if p.get("raw")), key=lambda p: {"ahd-5": 0, "IPA": 1}.get(p.get("rawType"), 2))
        return next((p["raw"].strip("/") for p in ranked), "screw flanders")

    def get_embed(self, definitions: List[dict]) -> discord.Embed:
        word = definitions[0].get("word")
        pronunciation = self.get_pronunciation(word)
        embed = discord.Embed(title=word)
        for category in sorted({d.get("partOfSpeech") or "word" for d in definitions}):
            lines = self.category_lines(word, [d for d in definitions if (d.get("partOfSpeech") or "word") == category])
            value = "\n".join(lines)
            if len(value) > MAX_FIELD_VALUE_LENGTH:
                value = f"{value[: MAX_FIELD_VALUE_LENGTH - 3]}..."
            embed.add_field(name=f"{category}: **{word}**  /{pronunciation}/", value=value, inline=False)
        return embed.set_footer(text=definitions[0].get("attributionText"))

    def category_lines(self, word: str, definitions: List[dict]) -> List[str]:
        fallback = f"this is where I'd use {word} in a sentence... IF I HAD ONE"
        lines = []
        for n, definition in enumerate(definitions, start=1):
            example = next((eu.get("text") for eu in (definition.get("exampleUses") or []) if eu.get("text")), fallback)
            lines.append(f"{n}. {self.plain_text(definition['text'])}\n_{self.plain_text(example)}_")
            lines.append("")
        return lines

    def plain_text(self, text: str) -> str:
        """Wiktionary and friends include html like <xref> in their text."""
        return html.unescape(re.sub(r"<[^>]+>", "", text))
