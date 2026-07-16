from datetime import datetime, time
from typing import List, Optional

import discord
import requests
from discord import ChannelType
from discord.ext import commands, tasks
from discord.utils import get

from duckbot.util.datetime import now, timezone

FREE_GAMES_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
STORE_PAGE_URL = "https://store.epicgames.com/en-CA/p"
THURSDAY = 3


class EpicGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.free_games_loop.start()

    def cog_unload(self):
        self.free_games_loop.cancel()

    def get_games_channel(self):
        return get(self.bot.get_all_channels(), guild__name="Friends Chat", name="games", type=ChannelType.text)

    @commands.command(name="epic")
    async def epic(self, context: commands.Context):
        embeds = self.get_free_games()
        if embeds:
            await context.send(embeds=embeds)
        else:
            await context.send("no free games right now, somehow")

    @tasks.loop(time=time(hour=12, tzinfo=timezone()))
    async def free_games_loop(self):
        await self.announce_free_games()

    async def announce_free_games(self):
        if now().weekday() == THURSDAY and (embeds := self.get_free_games()):
            await self.get_games_channel().send(embeds=embeds)

    def get_free_games(self) -> List[discord.Embed]:
        params = {"locale": "en-CA", "country": "CA", "allowCountries": "CA"}
        response = requests.get(FREE_GAMES_URL, params=params, timeout=(3.05, 27)).json()
        games = response["data"]["Catalog"]["searchStore"]["elements"]
        return [self.to_embed(game, offer) for game in games if (offer := self.free_offer(game))]

    def free_offer(self, game: dict) -> Optional[dict]:
        """Returns the game's active 100%-off promotion, if any."""
        if game.get("price", {}).get("totalPrice", {}).get("discountPrice") != 0:
            return None
        offers = [offer for promo in (game.get("promotions") or {}).get("promotionalOffers") or [] for offer in promo["promotionalOffers"]]
        return next((offer for offer in offers if offer["discountSetting"]["discountPercentage"] == 0), None)

    def to_embed(self, game: dict, offer: dict) -> discord.Embed:
        embed = discord.Embed(title=game["title"], url=self.store_page(game), description=game.get("description"))
        image = next((img["url"] for img in game.get("keyImages") or [] if img["type"] == "OfferImageWide"), None)
        if image:
            embed.set_image(url=image)
        end = int(datetime.fromisoformat(offer["endDate"]).timestamp())
        embed.add_field(name="Free until", value=f"<t:{end}:R>")
        embed.add_field(name="Original price", value=game["price"]["totalPrice"]["fmtPrice"]["originalPrice"])
        return embed

    def store_page(self, game: dict) -> str:
        mappings = (game.get("offerMappings") or []) + ((game.get("catalogNs") or {}).get("mappings") or [])
        slug = next((m["pageSlug"] for m in mappings if m.get("pageSlug")), game.get("productSlug"))
        return f"{STORE_PAGE_URL}/{slug}"

    @free_games_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
