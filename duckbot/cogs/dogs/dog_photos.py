from typing import List, Optional

import requests
from discord.ext import commands


class DogPhotos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dog", aliases=["doge"])
    async def dog_command(self, context, *, breed: Optional[str] = None):
        await self.dog(context, breed)

    async def dog(self, context, breed: Optional[str]):
        if breed and breed in self.get_breeds():
            await context.send(self.get_dog_image(breed))
        else:
            await context.send(self.get_dog_image(None))

    def get_dog_image(self, breed: Optional[str] = None) -> str:
        if breed:
            if " " in breed:
                path = f"breed/{'/'.join(reversed(breed.split()))}/images"
            else:
                path = f"breed/{breed}/images"
        else:
            path = f"breed/{breed.replace(' ', '/')}/images" if breed else "breeds/image"
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
