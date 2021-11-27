import os
from typing import List, Tuple

import discord
import requests
from discord.ext import commands

from duckbot.slash import Option, slash_command


class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.headers = {"app_id": os.getenv("OXFORD_DICTIONARY_ID"), "app_key": os.getenv("OXFORD_DICTIONARY_KEY")}
        self.url = "https://od-api.oxforddictionaries.com/api/v2"

    @slash_command(options=[Option(name="word", description="The word to define.", required=True)])
    @commands.command(name="define", description="Define a brother, word.")
    async def define_command(self, context, *, word: str = "taco"):
        await self.define(context, word)

    async def define(self, context, word: str):
        roots = self.get_root_words(word.lower())
        await context.send(embeds=[self.get_definition(x) for x in roots])

    def get_root_words(self, word: str) -> List[str]:
        """Returns all roots of the given word."""
        response = requests.get(f"{self.url}/lemmas/en/{word}", headers=self.headers).json()
        results = response.get("results", [])
        inflections = [i.get("id") for r in results for lex in r.get("lexicalEntries", []) for i in lex.get("inflectionOf", [])]
        return sorted(set(inflections))

    def get_definition(self, word: str) -> discord.Embed:
        """Returns the full definition of the word as an embed."""
        embed = discord.Embed(title=word)
        response = requests.get(f"{self.url}/entries/en-us/{word}", headers=self.headers).json()
        results = response.get("results", [])
        categories = sorted(set(lex.get("lexicalCategory", {}).get("id", None) for r in results for lex in r.get("lexicalEntries", [])))
        for category in categories:
            text, pronunciation, lines = self.category_group_data(word, category, results)
            embed.add_field(name=f"{category}: **{text}**  /{pronunciation}/", value="\n".join(lines), inline=False)

        return embed

    def category_group_data(self, word: str, category: str, results: List[dict]) -> Tuple[str, str, List[str]]:
        lines = []
        n = 0
        text = word
        pronunciation = "screw flanders"
        for result in results:
            for lex in result.get("lexicalEntries", []):
                if lex.get("lexicalCategory", {}).get("id", None) == category:
                    text, pronunciation, lex_lines, count = self.definition_data(word, lex, n)
                    n += count
                    lines = lines + lex_lines
        return text, pronunciation, lines

    def definition_data(self, word: str, lexical_entry: dict, entry_number: int) -> Tuple[str, str, List[str], int]:
        lines = []
        text = lexical_entry.get("text", word)
        pronunciation = "screw flanders"
        n = entry_number
        for entry in lexical_entry.get("entries", []):
            pronunciation, entry_lines, count = self.entry_data(entry, n)
            n += count
            lines = lines + entry_lines
        return text, pronunciation, lines, n

    def entry_data(self, entry: dict, entry_number: int) -> Tuple[str, List[str], int]:
        lines = []
        n = entry_number
        pronunciation = next((x.get("phoneticSpelling", "") for x in entry.get("pronunciations", []) if x.get("phoneticNotation", "") == "respell"), "")
        for sense in entry.get("senses", []):
            n += 1
            definition = next(iter(sense.get("definitions", [])), "it means things")
            example = next(iter(sense.get("examples", [])), {}).get("text", "this is where I'd use it in a sentence... IF I HAD ONE")
            lines.append(f"{n}. {definition}\n_{example}_") if example else lines.append(f"{n}. {definition}")
            for sub in sense.get("subsenses", []):
                definition = next(iter(sub.get("definitions", [])), "")
                example = next(iter(sub.get("examples", [])), {}).get("text", "")
                if definition:
                    lines.append(f"  • {definition}\n    _{example}_") if example else lines.append(f"  • {definition}")
            lines.append("")
        return pronunciation, lines, n
