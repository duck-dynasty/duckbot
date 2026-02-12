import random
from datetime import date
from typing import List, Optional

import discord
import requests
from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands

ANCHOR_DATE = date(2020, 12, 3)
POTD_SEED = 80081355

TYPE_COLORS = {
    "normal": 0xA8A77A,
    "fire": 0xEE8130,
    "water": 0x6390F0,
    "electric": 0xF7D02C,
    "grass": 0x7AC74C,
    "ice": 0x96D9D6,
    "fighting": 0xC22E28,
    "poison": 0xA33EA1,
    "ground": 0xE2BF65,
    "flying": 0xA98FF3,
    "psychic": 0xF95587,
    "bug": 0xA6B91A,
    "rock": 0xB6A136,
    "ghost": 0x735797,
    "dragon": 0x6F35FC,
    "dark": 0x705746,
    "steel": 0xB7B7CE,
    "fairy": 0xD685AD,
}


class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._pokemon_count = None
        self._pokemon_names = None

    @property
    def pokemon_count(self) -> int:
        if self._pokemon_count is None:
            result = requests.get("https://pokeapi.co/api/v2/pokemon-species?limit=1").json()
            self._pokemon_count = result["count"]
        return self._pokemon_count

    @property
    def pokemon_names(self) -> List[str]:
        if self._pokemon_names is None:
            result = requests.get(f"https://pokeapi.co/api/v2/pokemon-species?limit={self.pokemon_count}").json()
            self._pokemon_names = [entry["name"] for entry in result["results"]]
        return self._pokemon_names

    @commands.hybrid_command(name="pokemon", description="Show a Pokemon by name or ID. No args gives the Pokemon of the Day.")
    async def pokemon_command(self, context: commands.Context, *, name_or_id: Optional[str] = None):
        """
        :param name: The name of the Pokemon to show.
        :param id: The Pokedex ID of the Pokemon to show.
        """
        await self.pokemon(context, name_or_id)

    async def pokemon(self, context: commands.Context, name_or_id: Optional[str]):
        async with context.typing():
            try:
                if name_or_id is not None:
                    query = name_or_id.strip().lower()
                else:
                    query = str(self._get_pokemon_of_the_day_id())

                is_potd = name_or_id is None
                data = self.get_pokemon(query)
                species = self.get_species(data["species"]["url"])
                embed = self.build_embed(data, species, is_potd=is_potd)
                await context.send(embed=embed)
            except requests.exceptions.HTTPError:
                lookup = name_or_id if name_or_id is not None else str(id)
                await context.send(f"Could not find a Pokemon named '{lookup}'.")

    def _get_pokemon_of_the_day_id(self) -> int:
        n = self.pokemon_count
        ids = list(range(1, n + 1))
        rng = random.Random(POTD_SEED)
        rng.shuffle(ids)
        days_since_anchor = (date.today() - ANCHOR_DATE).days
        return ids[days_since_anchor % n]

    def get_pokemon(self, id_or_name: str) -> dict:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{id_or_name}")
        response.raise_for_status()
        return response.json()

    def get_species(self, url: str) -> dict:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def clean_flavor_text(text: str) -> str:
        return text.replace("\f", " ").replace("\n", " ").replace("\r", " ")

    @staticmethod
    def get_flavor_text(species: dict) -> str:
        entries = species.get("flavor_text_entries", [])
        for entry in reversed(entries):
            if entry.get("language", {}).get("name") == "en":
                return Pokemon.clean_flavor_text(entry["flavor_text"])
        return "No description available."

    @staticmethod
    def get_genus(species: dict) -> str:
        for entry in species.get("genera", []):
            if entry.get("language", {}).get("name") == "en":
                return entry["genus"]
        return ""

    def build_embed(self, data: dict, species: dict, is_potd: bool = False) -> discord.Embed:
        name = data["name"].capitalize()
        pokemon_id = data["id"]
        types = [t["type"]["name"] for t in data["types"]]
        primary_type = types[0]

        title = f"#{pokemon_id} \u2014 {name}"
        if is_potd:
            title = f"Pokemon of the Day: {title}"

        color = TYPE_COLORS.get(primary_type, 0x000000)
        embed = discord.Embed(title=title, color=color)

        genus = self.get_genus(species)
        flavor = self.get_flavor_text(species)
        description = f"*{genus}*\n\n{flavor}" if genus else flavor
        embed.description = description

        embed.add_field(name="Type", value=" / ".join(t.capitalize() for t in types), inline=True)

        height_m = data["height"] / 10
        weight_kg = data["weight"] / 10
        embed.add_field(name="Height / Weight", value=f"{height_m:.1f} m / {weight_kg:.1f} kg", inline=True)

        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        stat_lines = [
            f"HP: {stats.get('hp', '?')}",
            f"Atk: {stats.get('attack', '?')}",
            f"Def: {stats.get('defense', '?')}",
            f"Sp.Atk: {stats.get('special-attack', '?')}",
            f"Sp.Def: {stats.get('special-defense', '?')}",
            f"Speed: {stats.get('speed', '?')}",
        ]
        embed.add_field(name="Base Stats", value="\n".join(stat_lines), inline=True)

        sprite_url = data.get("sprites", {}).get("front_default")
        if sprite_url:
            embed.set_thumbnail(url=sprite_url)

        return embed

    @pokemon_command.autocomplete("name_or_id")
    async def pokemon_name_autocomplete(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        if len(current) < 3:
            return []
        lower = current.lower()
        return [Choice(name=n, value=n) for n in self.pokemon_names if lower in n][:25]
