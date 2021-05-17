import json
import urllib

from discord.ext import commands

from duckbot.slash import slash_command


class DogPhotos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO add breed option https://dog.ceo/dog-api/documentation/
    @slash_command()
    @commands.command(name="dog", description=":dog:")
    async def dog_command(self, context):
        await context.send(self.get_dog_image())

    def get_dog_image(self):
        req = urllib.request.Request("https://dog.ceo/api/breeds/image/random")
        req.add_header("Cookie", "euConsent=true")
        result = json.loads(urllib.request.urlopen(req).read())
        if result.get("status", "ded") != "success" or not result.get("message", None):
            raise RuntimeError("could not fetch a puppy")
        else:
            return result.get("message")
