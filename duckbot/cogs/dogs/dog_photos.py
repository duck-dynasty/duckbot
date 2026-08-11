from typing import List, Optional

import requests
from discord import Interaction
from discord.app_commands import Choice
from discord.ext import commands

from duckbot.util.choices import choices


class DogPhotos(commands.Cog):
    def __init__(self):
        self._breeds = None

    @property
    def breeds(self) -> List[str]:
        if self._breeds is None:
            self._breeds = self.get_breeds()
        return self._breeds

    @commands.hybrid_command(name="dog", aliases=["doge"], description="Show a random dog you probably don't know")
    async def dog(self, context: commands.Context, *, breed: Optional[str] = None):
        """
        :param breed: The specific breed of dog to show. Defaults to any breed.
        """
        async with context.typing():
            if breed and breed in self.breeds:
                await context.send(self.get_dog_image(breed))
            else:
                await context.send(self.get_dog_image(None))

    def get_dog_image(self, breed: Optional[str] = None) -> str:
        if breed:
            path = f"breed/{'/'.join(reversed(breed.split()))}/images"
        else:
            path = "breeds/image"
        result = requests.get(f"https://dog.ceo/api/{path}/random").json()
        if result.get("status", "ded") != "success" or not result.get("message", None):
            raise RuntimeError(f"could not fetch a puppy; breed = {breed}")
        else:
            return result.get("message")

    def get_breeds(self) -> List[str]:
        result = requests.get("https://dog.ceo/api/breeds/list/all").json()
        if result.get("status", "ded") != "success" or not result.get("message", None):
            raise RuntimeError("could not fetch a puppy")
        else:
            breeds = []
            for breed, sub_breeds in result.get("message").items():
                breeds.append(breed)
                for sub in sub_breeds:
                    breeds.append(f"{sub} {breed}")
            return breeds

    @dog.autocomplete("breed")
    async def breed_autocomplete(self, interaction: Interaction, current: str) -> List[Choice[str]]:
        return choices(self.breeds, current, min_characters=0)
